import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, Clock, AlertCircle, ArrowLeft, ArrowRight } from 'lucide-react'
import { AnnotationTask, EvaluationRubric, Annotation } from '@/types/annotation'
// import { OptimizationResults } from '@/types/optimization'
import { AnnotationForm } from './AnnotationForm'
import { ResultViewer } from './ResultViewer'

interface AnnotationInterfaceProps {
  task: AnnotationTask
  rubric: EvaluationRubric
  annotatorId: string
  onAnnotationComplete: (annotation: Annotation) => void
  onTaskComplete: () => void
}

export const AnnotationInterface: React.FC<AnnotationInterfaceProps> = ({
  task,
  rubric,
  annotatorId,
  onAnnotationComplete,
  onTaskComplete
}) => {
  const [currentResultIndex, setCurrentResultIndex] = useState(0)
  const [annotations, setAnnotations] = useState<Map<string, Annotation>>(new Map())
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [startTime, setStartTime] = useState<Date>(new Date())

  const currentResult = task.results[currentResultIndex]
  const totalResults = task.results.length
  const completedCount = annotations.size
  const progress = (completedCount / totalResults) * 100

  useEffect(() => {
    setStartTime(new Date())
  }, [currentResultIndex])

  const handleAnnotationSubmit = async (scores: Record<string, number>, comments: string, confidence: number) => {
    setIsSubmitting(true)
    
    try {
      const timeSpent = Math.floor((new Date().getTime() - startTime.getTime()) / 1000)
      
      const annotation: Annotation = {
        id: `${task.id}-${currentResult.task_id}-${annotatorId}`,
        task_id: task.id,
        annotator_id: annotatorId,
        result_id: currentResult.task_id,
        rubric_id: rubric.id,
        scores,
        comments,
        confidence,
        time_spent: timeSpent,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }

      // Store annotation locally
      const newAnnotations = new Map(annotations)
      newAnnotations.set(currentResult.task_id, annotation)
      setAnnotations(newAnnotations)

      // Submit to backend
      await onAnnotationComplete(annotation)

      // Move to next result or complete task
      if (currentResultIndex < totalResults - 1) {
        setCurrentResultIndex(currentResultIndex + 1)
      } else {
        onTaskComplete()
      }
    } catch (error) {
      console.error('Failed to submit annotation:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handlePrevious = () => {
    if (currentResultIndex > 0) {
      setCurrentResultIndex(currentResultIndex - 1)
    }
  }

  const handleNext = () => {
    if (currentResultIndex < totalResults - 1) {
      setCurrentResultIndex(currentResultIndex + 1)
    }
  }

  const getResultStatus = (resultId: string) => {
    return annotations.has(resultId) ? 'completed' : 'pending'
  }

  return (
    <div className="space-y-6">
      {/* Task Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                {task.name}
                <Badge variant={task.status === 'completed' ? 'default' : 'secondary'}>
                  {task.status}
                </Badge>
              </CardTitle>
              <CardDescription>{task.description}</CardDescription>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">
                Result {currentResultIndex + 1} of {totalResults}
              </div>
              <div className="text-lg font-semibold">
                {Math.round(progress)}% Complete
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Progress value={progress} className="w-full" />
            
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                {completedCount} completed
              </span>
              <span className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-yellow-500" />
                {totalResults - completedCount} remaining
              </span>
            </div>

            {task.deadline && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Deadline: {new Date(task.deadline).toLocaleDateString()}
                </AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentResultIndex === 0}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Previous
        </Button>

        <div className="flex items-center gap-2">
          {task.results.map((result, index) => (
            <Button
              key={result.task_id}
              variant={index === currentResultIndex ? 'default' : 'outline'}
              size="sm"
              onClick={() => setCurrentResultIndex(index)}
              className="relative"
            >
              {index + 1}
              {getResultStatus(result.task_id) === 'completed' && (
                <CheckCircle className="absolute -top-1 -right-1 h-3 w-3 text-green-500 bg-white rounded-full" />
              )}
            </Button>
          ))}
        </div>

        <Button
          variant="outline"
          onClick={handleNext}
          disabled={currentResultIndex === totalResults - 1}
        >
          Next
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Result Viewer */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Optimization Results</CardTitle>
              <CardDescription>
                Review the original and optimized outputs for this result
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResultViewer result={currentResult} />
            </CardContent>
          </Card>
        </div>

        {/* Annotation Form */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Evaluation Form</CardTitle>
              <CardDescription>
                Score this result according to the evaluation rubric
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AnnotationForm
                rubric={rubric}
                existingAnnotation={annotations.get(currentResult.task_id)}
                onSubmit={handleAnnotationSubmit}
                isSubmitting={isSubmitting}
              />
            </CardContent>
          </Card>
        </div>
      </div>

      <Separator />

      {/* Rubric Reference */}
      <Card>
        <CardHeader>
          <CardTitle>Evaluation Rubric</CardTitle>
          <CardDescription>
            Reference guide for scoring each dimension
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {rubric.dimensions.map((dimension) => (
              <div key={dimension.id} className="space-y-2">
                <h4 className="font-medium">{dimension.name}</h4>
                <p className="text-sm text-muted-foreground">{dimension.description}</p>
                <div className="space-y-1">
                  {dimension.criteria.map((criteria) => (
                    <div key={criteria.score} className="text-xs">
                      <span className="font-medium">{criteria.score}:</span> {criteria.description}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
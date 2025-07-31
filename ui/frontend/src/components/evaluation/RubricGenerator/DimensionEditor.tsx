import React, { useState, useEffect } from 'react'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card'
import { 
  Button 
} from '@/components/ui/button'
import { 
  Input 
} from '@/components/ui/input'
import { 
  Label 
} from '@/components/ui/label'
import { 
  Textarea 
} from '@/components/ui/textarea'
import { 
  Badge 
} from '@/components/ui/badge'
import { 
  Alert, 
  AlertDescription 
} from '@/components/ui/alert'
import { 
  Separator 
} from '@/components/ui/separator'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { 
  Slider 
} from '@/components/ui/slider'
import { 
  Plus, 
  Trash2, 
  Edit3, 
  Save, 
  AlertCircle,
  GripVertical,
  Settings
} from 'lucide-react'
import { 
  EvaluationRubric, 
  RubricDimension,
  RubricCriteria,
  ScoringScale 
} from '@/types'

interface DimensionEditorProps {
  rubric: EvaluationRubric
  onUpdate: (rubric: EvaluationRubric) => void
  onSave: () => void
  className?: string
}

interface DimensionFormData {
  name: string
  description: string
  weight: number
  criteria: RubricCriteria[]
}

const DimensionEditor: React.FC<DimensionEditorProps> = ({
  rubric,
  onUpdate,
  onSave,
  className
}) => {
  const [dimensions, setDimensions] = useState<RubricDimension[]>(rubric.dimensions)
  const [editingDimension, setEditingDimension] = useState<RubricDimension | null>(null)
  const [isAddingDimension, setIsAddingDimension] = useState(false)
  const [formData, setFormData] = useState<DimensionFormData>({
    name: '',
    description: '',
    weight: 1,
    criteria: []
  })
  const [hasChanges, setHasChanges] = useState(false)

  // Initialize criteria based on scoring scale
  const initializeCriteria = (scale: ScoringScale): RubricCriteria[] => {
    const criteria: RubricCriteria[] = []
    for (let i = scale.min_score; i <= scale.max_score; i++) {
      criteria.push({
        score: i,
        description: '',
        examples: []
      })
    }
    return criteria
  }

  const handleAddDimension = () => {
    setFormData({
      name: '',
      description: '',
      weight: 1,
      criteria: initializeCriteria(rubric.scoring_scale)
    })
    setEditingDimension(null)
    setIsAddingDimension(true)
  }

  const handleEditDimension = (dimension: RubricDimension) => {
    setFormData({
      name: dimension.name,
      description: dimension.description,
      weight: dimension.weight,
      criteria: [...dimension.criteria]
    })
    setEditingDimension(dimension)
    setIsAddingDimension(true)
  }

  const handleSaveDimension = () => {
    if (!formData.name.trim()) return

    const newDimension: RubricDimension = {
      id: editingDimension?.id || `dim_${Date.now()}`,
      name: formData.name,
      description: formData.description,
      weight: formData.weight,
      criteria: formData.criteria
    }

    let updatedDimensions: RubricDimension[]
    
    if (editingDimension) {
      updatedDimensions = dimensions.map(dim => 
        dim.id === editingDimension.id ? newDimension : dim
      )
    } else {
      updatedDimensions = [...dimensions, newDimension]
    }

    setDimensions(updatedDimensions)
    setHasChanges(true)
    setIsAddingDimension(false)
    setEditingDimension(null)
    
    // Update parent component
    const updatedRubric = {
      ...rubric,
      dimensions: updatedDimensions
    }
    onUpdate(updatedRubric)
  }

  const handleDeleteDimension = (dimensionId: string) => {
    const updatedDimensions = dimensions.filter(dim => dim.id !== dimensionId)
    setDimensions(updatedDimensions)
    setHasChanges(true)
    
    const updatedRubric = {
      ...rubric,
      dimensions: updatedDimensions
    }
    onUpdate(updatedRubric)
  }

  const handleCriteriaChange = (index: number, field: keyof RubricCriteria, value: any) => {
    const updatedCriteria = [...formData.criteria]
    updatedCriteria[index] = {
      ...updatedCriteria[index],
      [field]: value
    }
    setFormData(prev => ({
      ...prev,
      criteria: updatedCriteria
    }))
  }

  const addExample = (criteriaIndex: number) => {
    const updatedCriteria = [...formData.criteria]
    if (!updatedCriteria[criteriaIndex].examples) {
      updatedCriteria[criteriaIndex].examples = []
    }
    updatedCriteria[criteriaIndex].examples!.push('')
    setFormData(prev => ({
      ...prev,
      criteria: updatedCriteria
    }))
  }

  const updateExample = (criteriaIndex: number, exampleIndex: number, value: string) => {
    const updatedCriteria = [...formData.criteria]
    if (updatedCriteria[criteriaIndex].examples) {
      updatedCriteria[criteriaIndex].examples![exampleIndex] = value
    }
    setFormData(prev => ({
      ...prev,
      criteria: updatedCriteria
    }))
  }

  const removeExample = (criteriaIndex: number, exampleIndex: number) => {
    const updatedCriteria = [...formData.criteria]
    if (updatedCriteria[criteriaIndex].examples) {
      updatedCriteria[criteriaIndex].examples!.splice(exampleIndex, 1)
    }
    setFormData(prev => ({
      ...prev,
      criteria: updatedCriteria
    }))
  }

  const getTotalWeight = () => {
    return dimensions.reduce((sum, dim) => sum + dim.weight, 0)
  }

  const isWeightValid = () => {
    const total = getTotalWeight()
    return total > 0 && total <= 10 // Reasonable weight limit
  }

  useEffect(() => {
    setDimensions(rubric.dimensions)
  }, [rubric.dimensions])

  return (
    <div className={`space-y-6 ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Dimension Editor
            </div>
            <div className="flex items-center gap-2">
              {hasChanges && (
                <Badge variant="outline" className="text-orange-600">
                  Unsaved Changes
                </Badge>
              )}
              <Button onClick={onSave} disabled={!hasChanges}>
                <Save className="mr-2 h-4 w-4" />
                Save Rubric
              </Button>
            </div>
          </CardTitle>
          <CardDescription>
            Customize evaluation dimensions and scoring criteria for your rubric
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-sm font-medium">Total Weight Distribution</Label>
              <div className="flex items-center gap-2">
                <Badge variant={isWeightValid() ? "default" : "destructive"}>
                  {getTotalWeight()}/10
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {isWeightValid() ? "Balanced" : "Needs adjustment"}
                </span>
              </div>
            </div>
            <Button onClick={handleAddDimension}>
              <Plus className="mr-2 h-4 w-4" />
              Add Dimension
            </Button>
          </div>

          {!isWeightValid() && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Total dimension weights should be between 1 and 10 for optimal evaluation balance
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-4">
            {dimensions.map((dimension) => (
              <Card key={dimension.id} className="relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <GripVertical className="h-4 w-4 text-muted-foreground cursor-move" />
                      <div>
                        <CardTitle className="text-base">{dimension.name}</CardTitle>
                        <CardDescription className="text-sm">
                          {dimension.description}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">
                        Weight: {dimension.weight}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditDimension(dimension)}
                      >
                        <Edit3 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteDimension(dimension.id)}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Scoring Criteria</Label>
                    <div className="grid gap-2">
                      {dimension.criteria.map((criteria, criteriaIndex) => (
                        <div key={criteriaIndex} className="flex items-start gap-3 p-2 bg-muted/50 rounded">
                          <Badge variant="secondary" className="min-w-[32px] justify-center mt-1">
                            {criteria.score}
                          </Badge>
                          <div className="flex-1 text-sm">
                            {criteria.description || (
                              <span className="text-muted-foreground italic">
                                No description provided
                              </span>
                            )}
                            {criteria.examples && criteria.examples.length > 0 && (
                              <div className="mt-1 space-y-1">
                                {criteria.examples.map((example, exampleIndex) => (
                                  <div key={exampleIndex} className="text-xs text-muted-foreground">
                                    • {example}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            {dimensions.length === 0 && (
              <Card>
                <CardContent className="flex items-center justify-center py-8">
                  <div className="text-center space-y-2">
                    <Settings className="h-8 w-8 text-muted-foreground mx-auto" />
                    <p className="text-muted-foreground">No dimensions defined</p>
                    <p className="text-sm text-muted-foreground">Add dimensions to start building your rubric</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Dimension Form Dialog */}
      <Dialog open={isAddingDimension} onOpenChange={setIsAddingDimension}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingDimension ? 'Edit Dimension' : 'Add New Dimension'}
            </DialogTitle>
            <DialogDescription>
              Define the evaluation dimension and its scoring criteria
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="dimension-name">Dimension Name</Label>
                <Input
                  id="dimension-name"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Accuracy, Clarity, Relevance"
                />
              </div>
              <div className="space-y-2">
                <Label>Weight ({formData.weight})</Label>
                <Slider
                  value={[formData.weight]}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, weight: value[0] }))}
                  max={5}
                  min={0.1}
                  step={0.1}
                  className="w-full"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dimension-description">Description</Label>
              <Textarea
                id="dimension-description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe what this dimension evaluates"
                rows={2}
              />
            </div>

            <Separator />

            <div className="space-y-4">
              <Label className="text-base font-medium">Scoring Criteria</Label>
              <div className="space-y-4">
                {formData.criteria.map((criteria, index) => (
                  <Card key={index} className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Badge variant="default" className="min-w-[32px] justify-center">
                          {criteria.score}
                        </Badge>
                        <Label className="text-sm font-medium">
                          Score {criteria.score} Description
                        </Label>
                      </div>
                      
                      <Textarea
                        value={criteria.description}
                        onChange={(e) => handleCriteriaChange(index, 'description', e.target.value)}
                        placeholder={`Describe what qualifies for a score of ${criteria.score}`}
                        rows={2}
                      />

                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label className="text-sm">Examples (optional)</Label>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => addExample(index)}
                          >
                            <Plus className="h-3 w-3 mr-1" />
                            Add Example
                          </Button>
                        </div>
                        
                        {criteria.examples && criteria.examples.map((example, exampleIndex) => (
                          <div key={exampleIndex} className="flex items-center gap-2">
                            <Input
                              value={example}
                              onChange={(e) => updateExample(index, exampleIndex, e.target.value)}
                              placeholder="Example of this score level"
                              className="text-sm"
                            />
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeExample(index, exampleIndex)}
                              className="text-destructive hover:text-destructive"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddingDimension(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveDimension} disabled={!formData.name.trim()}>
              <Save className="mr-2 h-4 w-4" />
              {editingDimension ? 'Update Dimension' : 'Add Dimension'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default DimensionEditor
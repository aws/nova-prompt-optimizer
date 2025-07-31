import React, { useState, useEffect } from 'react'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs'
import { 
  Badge 
} from '@/components/ui/badge'
import { 
  Alert, 
  AlertDescription 
} from '@/components/ui/alert'
import { 
  Progress 
} from '@/components/ui/progress'
import { 
  Separator 
} from '@/components/ui/separator'
import { 
  LoadingSpinner 
} from '@/components/common/Loading'
import { 
  Brain, 
  Wand2, 
  Eye, 
  Save, 
  TestTube, 
  AlertCircle,
  CheckCircle,
  BarChart3,
  FileText,
  Settings
} from 'lucide-react'
import { 
  EvaluationRubric, 
  Dataset
} from '@/types'
import { useAnnotation } from '@/hooks'
import { useDataset } from '@/hooks'
import DimensionEditor from './DimensionEditor'

interface RubricGeneratorProps {
  dataset?: Dataset
  onRubricGenerated?: (rubric: EvaluationRubric) => void
  onRubricSaved?: (rubric: EvaluationRubric) => void
  className?: string
}

interface DatasetAnalysis {
  total_samples: number
  unique_outputs: number
  avg_input_length: number
  avg_output_length: number
  detected_patterns: string[]
  suggested_dimensions: string[]
  complexity_score: number
}

const RubricGenerator: React.FC<RubricGeneratorProps> = ({
  dataset,
  onRubricGenerated,
  onRubricSaved,
  className
}) => {
  const { generateRubric, currentRubric, updateRubric } = useAnnotation()
  const { datasets } = useDataset()
  
  const [selectedDataset, setSelectedDataset] = useState<Dataset | undefined>(dataset)
  const [rubricName, setRubricName] = useState('')
  const [rubricDescription, setRubricDescription] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [datasetAnalysis, setDatasetAnalysis] = useState<DatasetAnalysis | null>(null)
  const [activeTab, setActiveTab] = useState('analyze')

  const [testResults, setTestResults] = useState<any>(null)

  // Mock dataset analysis (in real implementation, this would call the backend)
  const analyzeDataset = async (datasetToAnalyze: Dataset) => {
    setIsGenerating(true)
    setAnalysisProgress(0)
    
    // Simulate analysis progress
    const progressInterval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock analysis results
      const analysis: DatasetAnalysis = {
        total_samples: datasetToAnalyze.row_count || 100,
        unique_outputs: Math.floor((datasetToAnalyze.row_count || 100) * 0.8),
        avg_input_length: 150,
        avg_output_length: 75,
        detected_patterns: [
          'Question-Answer format',
          'Classification labels',
          'Sentiment indicators',
          'Technical terminology'
        ],
        suggested_dimensions: [
          'Accuracy',
          'Completeness',
          'Clarity',
          'Relevance',
          'Tone Appropriateness'
        ],
        complexity_score: 7.5
      }
      
      setDatasetAnalysis(analysis)
      setAnalysisProgress(100)
      setActiveTab('generate')
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      clearInterval(progressInterval)
      setIsGenerating(false)
    }
  }

  const handleGenerateRubric = async () => {
    if (!selectedDataset) return
    
    try {
      setIsGenerating(true)
      
      const config = {
        rubric_name: rubricName || `${selectedDataset.name} Evaluation Rubric`,
        description: rubricDescription || `AI-generated rubric for ${selectedDataset.name}`,
        suggested_dimensions: datasetAnalysis?.suggested_dimensions || [],
        complexity_score: datasetAnalysis?.complexity_score || 5
      }
      
      const rubric = await generateRubric(selectedDataset.id, config)
      
      if (onRubricGenerated) {
        onRubricGenerated(rubric)
      }
      
      setActiveTab('edit')
    } catch (error) {
      console.error('Rubric generation failed:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSaveRubric = async () => {
    if (!currentRubric.data) return
    
    try {
      const updates = {
        name: rubricName || currentRubric.data.name,
        description: rubricDescription || currentRubric.data.description
      }
      
      const updatedRubric = await updateRubric(currentRubric.data.id, updates)
      
      if (onRubricSaved) {
        onRubricSaved(updatedRubric)
      }
    } catch (error) {
      console.error('Save failed:', error)
    }
  }

  const handleTestRubric = async () => {
    if (!currentRubric.data || !selectedDataset) return
    
    // Mock testing with sample data
    setTestResults({
      sample_size: 10,
      avg_score: 4.2,
      dimension_scores: {
        'Accuracy': 4.5,
        'Completeness': 4.0,
        'Clarity': 4.3,
        'Relevance': 4.1
      },
      consistency_score: 0.85,
      issues: [
        'Dimension "Tone" may need clearer criteria',
        'Score distribution is slightly skewed toward higher scores'
      ]
    })
  }

  useEffect(() => {
    if (dataset) {
      setSelectedDataset(dataset)
    }
  }, [dataset])

  return (
    <div className={`space-y-6 ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            AI Rubric Generator
          </CardTitle>
          <CardDescription>
            Generate evaluation rubrics automatically by analyzing your dataset patterns and ground truth data
          </CardDescription>
        </CardHeader>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="analyze" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Analyze
          </TabsTrigger>
          <TabsTrigger value="generate" className="flex items-center gap-2">
            <Wand2 className="h-4 w-4" />
            Generate
          </TabsTrigger>
          <TabsTrigger value="edit" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Edit
          </TabsTrigger>
          <TabsTrigger value="preview" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Preview
          </TabsTrigger>
        </TabsList>

        <TabsContent value="analyze" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Dataset Analysis</CardTitle>
              <CardDescription>
                Select a dataset to analyze its patterns and generate appropriate evaluation dimensions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Select Dataset</Label>
                <Select 
                  value={selectedDataset?.id || ''} 
                  onValueChange={(value) => {
                    const dataset = datasets.data?.items.find(d => d.id === value)
                    setSelectedDataset(dataset)
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a dataset to analyze" />
                  </SelectTrigger>
                  <SelectContent>
                    {datasets.data?.items.map((dataset) => (
                      <SelectItem key={dataset.id} value={dataset.id}>
                        {dataset.name} ({dataset.row_count} rows)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {selectedDataset && !datasetAnalysis && (
                <Button 
                  onClick={() => analyzeDataset(selectedDataset)}
                  disabled={isGenerating}
                  className="w-full"
                >
                  {isGenerating ? (
                    <>
                      <LoadingSpinner className="mr-2 h-4 w-4" />
                      Analyzing Dataset...
                    </>
                  ) : (
                    <>
                      <BarChart3 className="mr-2 h-4 w-4" />
                      Analyze Dataset
                    </>
                  )}
                </Button>
              )}

              {isGenerating && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Analysis Progress</span>
                    <span>{analysisProgress}%</span>
                  </div>
                  <Progress value={analysisProgress} className="w-full" />
                </div>
              )}

              {datasetAnalysis && (
                <div className="space-y-4">
                  <Alert>
                    <CheckCircle className="h-4 w-4" />
                    <AlertDescription>
                      Dataset analysis completed successfully
                    </AlertDescription>
                  </Alert>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="text-sm font-medium">Dataset Statistics</Label>
                      <div className="space-y-1 text-sm">
                        <div>Total Samples: <Badge variant="outline">{datasetAnalysis.total_samples}</Badge></div>
                        <div>Unique Outputs: <Badge variant="outline">{datasetAnalysis.unique_outputs}</Badge></div>
                        <div>Avg Input Length: <Badge variant="outline">{datasetAnalysis.avg_input_length} chars</Badge></div>
                        <div>Complexity Score: <Badge variant="outline">{datasetAnalysis.complexity_score}/10</Badge></div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-sm font-medium">Detected Patterns</Label>
                      <div className="flex flex-wrap gap-1">
                        {datasetAnalysis.detected_patterns.map((pattern, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {pattern}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Suggested Evaluation Dimensions</Label>
                    <div className="flex flex-wrap gap-2">
                      {datasetAnalysis.suggested_dimensions.map((dimension, index) => (
                        <Badge key={index} variant="default" className="text-sm">
                          {dimension}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="generate" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Generate AI Rubric</CardTitle>
              <CardDescription>
                Configure and generate an evaluation rubric based on your dataset analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!datasetAnalysis ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Please analyze a dataset first before generating a rubric
                  </AlertDescription>
                </Alert>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="rubric-name">Rubric Name</Label>
                      <Input
                        id="rubric-name"
                        value={rubricName}
                        onChange={(e) => setRubricName(e.target.value)}
                        placeholder={`${selectedDataset?.name} Evaluation Rubric`}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Scoring Scale</Label>
                      <Select defaultValue="1-5">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1-3">1-3 Scale (Basic)</SelectItem>
                          <SelectItem value="1-5">1-5 Scale (Standard)</SelectItem>
                          <SelectItem value="1-10">1-10 Scale (Detailed)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="rubric-description">Description</Label>
                    <Textarea
                      id="rubric-description"
                      value={rubricDescription}
                      onChange={(e) => setRubricDescription(e.target.value)}
                      placeholder="Describe the purpose and scope of this evaluation rubric"
                      rows={3}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Based on Analysis</Label>
                    <div className="p-3 bg-muted rounded-lg text-sm">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-4 w-4" />
                        <span className="font-medium">{selectedDataset?.name}</span>
                      </div>
                      <div className="text-muted-foreground">
                        {datasetAnalysis.suggested_dimensions.length} dimensions suggested • 
                        Complexity: {datasetAnalysis.complexity_score}/10
                      </div>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
            <CardFooter>
              <Button 
                onClick={handleGenerateRubric}
                disabled={!datasetAnalysis || isGenerating || currentRubric.loading === 'loading'}
                className="w-full"
              >
                {currentRubric.loading === 'loading' ? (
                  <>
                    <LoadingSpinner className="mr-2 h-4 w-4" />
                    Generating Rubric...
                  </>
                ) : (
                  <>
                    <Wand2 className="mr-2 h-4 w-4" />
                    Generate AI Rubric
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="edit" className="space-y-4">
          {currentRubric.data ? (
            <DimensionEditor
              rubric={currentRubric.data}
              onUpdate={(updatedRubric) => {
                // Handle rubric updates
                console.log('Rubric updated:', updatedRubric)
              }}
              onSave={handleSaveRubric}
            />
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center py-8">
                <div className="text-center space-y-2">
                  <AlertCircle className="h-8 w-8 text-muted-foreground mx-auto" />
                  <p className="text-muted-foreground">No rubric to edit</p>
                  <p className="text-sm text-muted-foreground">Generate a rubric first to start editing</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="preview" className="space-y-4">
          {currentRubric.data ? (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    Rubric Preview
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={handleTestRubric}>
                        <TestTube className="mr-2 h-4 w-4" />
                        Test Rubric
                      </Button>
                      <Button size="sm" onClick={handleSaveRubric}>
                        <Save className="mr-2 h-4 w-4" />
                        Save Rubric
                      </Button>
                    </div>
                  </CardTitle>
                  <CardDescription>
                    Preview how your rubric will appear to annotators
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-lg">{currentRubric.data.name}</h3>
                    <p className="text-muted-foreground">{currentRubric.data.description}</p>
                  </div>

                  <Separator />

                  <div className="space-y-4">
                    <h4 className="font-medium">Evaluation Dimensions</h4>
                    {currentRubric.data.dimensions.map((dimension) => (
                      <Card key={dimension.id} className="p-4">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <h5 className="font-medium">{dimension.name}</h5>
                            <Badge variant="outline">Weight: {dimension.weight}</Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{dimension.description}</p>
                          
                          <div className="space-y-1">
                            <Label className="text-xs font-medium">Scoring Criteria:</Label>
                            <div className="grid gap-1">
                              {dimension.criteria.map((criteria, criteriaIndex) => (
                                <div key={criteriaIndex} className="flex items-start gap-2 text-sm">
                                  <Badge variant="secondary" className="text-xs min-w-[24px] justify-center">
                                    {criteria.score}
                                  </Badge>
                                  <span>{criteria.description}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>

                  {testResults && (
                    <>
                      <Separator />
                      <div className="space-y-3">
                        <h4 className="font-medium">Test Results</h4>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label className="text-sm">Overall Performance</Label>
                            <div className="space-y-1">
                              <div className="flex justify-between text-sm">
                                <span>Average Score:</span>
                                <Badge>{testResults.avg_score}/5</Badge>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span>Consistency:</span>
                                <Badge variant="outline">{(testResults.consistency_score * 100).toFixed(0)}%</Badge>
                              </div>
                            </div>
                          </div>
                          <div className="space-y-2">
                            <Label className="text-sm">Dimension Scores</Label>
                            <div className="space-y-1">
                              {Object.entries(testResults.dimension_scores).map(([dim, score]) => (
                                <div key={dim} className="flex justify-between text-sm">
                                  <span>{dim}:</span>
                                  <Badge variant="secondary">{String(score)}/5</Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                        
                        {testResults.issues.length > 0 && (
                          <Alert>
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>
                              <div className="space-y-1">
                                <div className="font-medium">Suggested Improvements:</div>
                                <ul className="list-disc list-inside space-y-1">
                                  {testResults.issues.map((issue: string, index: number) => (
                                    <li key={index} className="text-sm">{issue}</li>
                                  ))}
                                </ul>
                              </div>
                            </AlertDescription>
                          </Alert>
                        )}
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center py-8">
                <div className="text-center space-y-2">
                  <Eye className="h-8 w-8 text-muted-foreground mx-auto" />
                  <p className="text-muted-foreground">No rubric to preview</p>
                  <p className="text-sm text-muted-foreground">Generate a rubric first to see the preview</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default RubricGenerator
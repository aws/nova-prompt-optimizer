import { useState, useCallback, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { 
  Save, 
  Play,
  CheckCircle, 
  AlertTriangle, 
  Code, 
  Library,
  Download,
  Settings
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useMetrics } from '@/hooks'
import type { 
  CustomMetric, 
  MetricCreateRequest, 
  MetricUpdateRequest,
  MetricTestCase,
  MetricTemplate
} from '@/types/metric'
import { METRIC_TEMPLATES } from '@/types/metric'
import { CodeEditor } from './CodeEditor'
import { MetricTester } from './MetricTester'
import { MetricLibrary } from './MetricLibrary'

interface MetricBuilderProps {
  metric?: CustomMetric
  onSave?: (metric: CustomMetric) => void
  onCancel?: () => void
  className?: string
}

export function MetricBuilder({ 
  metric, 
  onSave, 
  onCancel,
  className 
}: MetricBuilderProps) {
  const {
    validationResult,
    testResult,
    loading,
    error,
    createMetric,
    updateMetric,
    validateMetric,
    testMetric,
    clearValidation,
    clearError
  } = useMetrics()

  // Form state
  const [formData, setFormData] = useState({
    name: metric?.name || '',
    description: metric?.description || '',
    code: metric?.code || '',
    tags: metric?.tags || [],
    is_public: metric?.is_public || false
  })

  // UI state
  const [showLibrary, setShowLibrary] = useState(false)
  const [testCases, setTestCases] = useState<MetricTestCase[]>([])
  const [newTag, setNewTag] = useState('')

  // Update form when metric prop changes
  useEffect(() => {
    if (metric) {
      setFormData({
        name: metric.name,
        description: metric.description,
        code: metric.code,
        tags: metric.tags || [],
        is_public: metric.is_public || false
      })
    }
  }, [metric])

  // Auto-validate code when it changes
  useEffect(() => {
    if (formData.code.trim()) {
      const timeoutId = setTimeout(() => {
        validateMetric(formData.code).catch(() => {
          // Validation errors are handled by the hook
        })
      }, 1000) // Debounce validation

      return () => clearTimeout(timeoutId)
    } else {
      clearValidation()
    }
  }, [formData.code, validateMetric, clearValidation])

  const handleInputChange = useCallback((field: keyof typeof formData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    clearError()
  }, [clearError])

  const handleAddTag = useCallback(() => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      handleInputChange('tags', [...formData.tags, newTag.trim()])
      setNewTag('')
    }
  }, [newTag, formData.tags, handleInputChange])

  const handleRemoveTag = useCallback((tagToRemove: string) => {
    handleInputChange('tags', formData.tags.filter(tag => tag !== tagToRemove))
  }, [formData.tags, handleInputChange])

  const handleTemplateSelect = useCallback((template: MetricTemplate) => {
    handleInputChange('code', METRIC_TEMPLATES[template])
  }, [handleInputChange])

  const handleSave = useCallback(async () => {
    try {
      if (!formData.name.trim()) {
        throw new Error('Metric name is required')
      }
      if (!formData.code.trim()) {
        throw new Error('Metric code is required')
      }

      const metricData: MetricCreateRequest | MetricUpdateRequest = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        code: formData.code.trim(),
        tags: formData.tags,
        is_public: formData.is_public
      }

      let savedMetric: CustomMetric
      if (metric?.id) {
        savedMetric = await updateMetric(metric.id, metricData)
      } else {
        savedMetric = await createMetric(metricData as MetricCreateRequest)
      }

      onSave?.(savedMetric)
    } catch (error) {
      // Error is handled by the hook
    }
  }, [formData, metric, createMetric, updateMetric, onSave])

  const handleTest = useCallback(async () => {
    if (!testCases.length) {
      return
    }

    try {
      await testMetric({
        code: formData.code,
        test_cases: testCases
      })
    } catch (error) {
      // Error is handled by the hook
    }
  }, [formData.code, testCases, testMetric])

  const isValid = validationResult?.is_valid ?? false
  const hasRequiredMethods = validationResult?.has_apply_method && validationResult?.has_batch_apply_method

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">
            {metric ? 'Edit Metric' : 'Create Custom Metric'}
          </h2>
          <p className="text-muted-foreground">
            Build and test custom evaluation metrics for your optimization tasks
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Dialog open={showLibrary} onOpenChange={setShowLibrary}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Library className="mr-2 h-4 w-4" />
                Library
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Metric Library</DialogTitle>
                <DialogDescription>
                  Browse and import metrics from the community library
                </DialogDescription>
              </DialogHeader>
              <MetricLibrary 
                onImport={(importedMetric) => {
                  setFormData({
                    name: importedMetric.name,
                    description: importedMetric.description,
                    code: importedMetric.code,
                    tags: importedMetric.tags || [],
                    is_public: false
                  })
                  setShowLibrary(false)
                }}
              />
            </DialogContent>
          </Dialog>
          {onCancel && (
            <Button variant="outline" onClick={onCancel}>
              Cancel
            </Button>
          )}
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Basic Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="metric-name">Name *</Label>
                  <Input
                    id="metric-name"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="e.g., Custom Accuracy Metric"
                    disabled={loading}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Visibility</Label>
                  <Select
                    value={formData.is_public ? 'public' : 'private'}
                    onValueChange={(value) => handleInputChange('is_public', value === 'public')}
                    disabled={loading}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="private">Private</SelectItem>
                      <SelectItem value="public">Public</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="metric-description">Description</Label>
                <Textarea
                  id="metric-description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Describe what this metric measures and how it works..."
                  rows={3}
                  disabled={loading}
                />
              </div>

              {/* Tags */}
              <div className="space-y-2">
                <Label>Tags</Label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {formData.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                      {tag}
                      <button
                        onClick={() => handleRemoveTag(tag)}
                        className="ml-1 hover:text-destructive"
                        disabled={loading}
                      >
                        ×
                      </button>
                    </Badge>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Input
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    placeholder="Add a tag..."
                    onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                    disabled={loading}
                  />
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={handleAddTag}
                    disabled={loading || !newTag.trim()}
                  >
                    Add
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Code Editor */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  Metric Implementation
                </div>
                <Select onValueChange={handleTemplateSelect} disabled={loading}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Use template..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="basic_accuracy">Basic Accuracy</SelectItem>
                    <SelectItem value="classification_f1">Classification F1</SelectItem>
                    <SelectItem value="text_similarity">Text Similarity</SelectItem>
                  </SelectContent>
                </Select>
              </CardTitle>
              <CardDescription>
                Implement your metric class with <code>apply()</code> and <code>batch_apply()</code> methods
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CodeEditor
                value={formData.code}
                onChange={(code) => handleInputChange('code', code)}
                language="python"
                placeholder="# Implement your custom metric class here..."
                disabled={loading}
                className="min-h-[400px]"
              />
            </CardContent>
          </Card>

          {/* Test Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Play className="h-5 w-5" />
                Test Metric
              </CardTitle>
              <CardDescription>
                Test your metric with sample data to ensure it works correctly
              </CardDescription>
            </CardHeader>
            <CardContent>
              <MetricTester
                code={formData.code}
                testCases={testCases}
                onTestCasesChange={setTestCases}
                onTest={handleTest}
                testResult={testResult}
                loading={loading}
              />
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Validation & Info */}
        <div className="space-y-6">
          {/* Validation Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {isValid ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-yellow-500" />
                )}
                Validation Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {validationResult ? (
                <>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Overall Status</span>
                      <Badge variant={isValid ? 'default' : 'destructive'}>
                        {isValid ? 'Valid' : 'Invalid'}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>apply() method</span>
                      <Badge variant={validationResult.has_apply_method ? 'default' : 'secondary'}>
                        {validationResult.has_apply_method ? 'Found' : 'Missing'}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>batch_apply() method</span>
                      <Badge variant={validationResult.has_batch_apply_method ? 'default' : 'secondary'}>
                        {validationResult.has_batch_apply_method ? 'Found' : 'Missing'}
                      </Badge>
                    </div>
                  </div>

                  {validationResult.detected_methods.length > 0 && (
                    <div className="space-y-2">
                      <Label className="text-sm font-medium">Detected Methods</Label>
                      <div className="flex flex-wrap gap-1">
                        {validationResult.detected_methods.map((method) => (
                          <Badge key={method} variant="outline" className="text-xs">
                            {method}()
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {validationResult.errors.length > 0 && (
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-destructive">Errors</Label>
                      <div className="space-y-1">
                        {validationResult.errors.map((error, index) => (
                          <div key={index} className="text-xs text-destructive bg-destructive/10 p-2 rounded">
                            {error}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {validationResult.warnings.length > 0 && (
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-yellow-600">Warnings</Label>
                      <div className="space-y-1">
                        {validationResult.warnings.map((warning, index) => (
                          <div key={index} className="text-xs text-yellow-700 bg-yellow-50 p-2 rounded">
                            {warning}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-sm text-muted-foreground text-center py-4">
                  Start typing code to see validation results
                </div>
              )}
            </CardContent>
          </Card>

          {/* Requirements */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Requirements</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="space-y-2">
                <div className="font-medium">Required Methods:</div>
                <ul className="space-y-1 text-muted-foreground">
                  <li>• <code>apply(prediction, ground_truth)</code></li>
                  <li>• <code>batch_apply(predictions, ground_truths)</code></li>
                </ul>
              </div>
              <Separator />
              <div className="space-y-2">
                <div className="font-medium">Return Types:</div>
                <ul className="space-y-1 text-muted-foreground">
                  <li>• <code>apply()</code>: float or dict</li>
                  <li>• <code>batch_apply()</code>: float or dict</li>
                </ul>
              </div>
              <Separator />
              <div className="space-y-2">
                <div className="font-medium">Best Practices:</div>
                <ul className="space-y-1 text-muted-foreground">
                  <li>• Handle edge cases gracefully</li>
                  <li>• Include proper error handling</li>
                  <li>• Add docstrings for clarity</li>
                  <li>• Test with various data types</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-3">
                <Button 
                  onClick={handleSave}
                  disabled={loading || !formData.name.trim() || !formData.code.trim() || !hasRequiredMethods}
                  className="w-full"
                >
                  <Save className="mr-2 h-4 w-4" />
                  {metric ? 'Update Metric' : 'Save Metric'}
                </Button>
                
                {metric && (
                  <Button 
                    variant="outline" 
                    onClick={() => {/* TODO: Implement export */}}
                    disabled={loading}
                    className="w-full"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Export Code
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default MetricBuilder
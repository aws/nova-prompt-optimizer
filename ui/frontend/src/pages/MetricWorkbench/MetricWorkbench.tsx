import React, { useState, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Plus, 
  Code, 
  Library, 
  Settings,
  Beaker,
  BookOpen
} from 'lucide-react'
import { MetricBuilder } from '@/components/evaluation'
import { useMetrics } from '@/hooks'
import type { CustomMetric } from '@/types/metric'

export function MetricWorkbench() {
  const {
    metrics,
    loading,
    error,
    loadMetrics,
    loadMetric,
    clearError
  } = useMetrics()

  const [activeTab, setActiveTab] = useState<'builder' | 'library' | 'templates'>('builder')
  const [selectedMetric, setSelectedMetric] = useState<CustomMetric | undefined>()
  const [showBuilder, setShowBuilder] = useState(false)

  // Load metrics on mount
  React.useEffect(() => {
    loadMetrics()
  }, [loadMetrics])

  // Handle metric selection
  const handleMetricSelect = useCallback(async (metric: CustomMetric) => {
    try {
      await loadMetric(metric.id)
      setSelectedMetric(metric)
      setShowBuilder(true)
      setActiveTab('builder')
    } catch (error) {
      // Error handled by hook
    }
  }, [loadMetric])

  // Handle new metric
  const handleNewMetric = useCallback(() => {
    setSelectedMetric(undefined)
    setShowBuilder(true)
    setActiveTab('builder')
  }, [])

  // Handle metric save
  const handleMetricSave = useCallback((metric: CustomMetric) => {
    setSelectedMetric(metric)
    loadMetrics() // Refresh the list
  }, [loadMetrics])

  // Handle cancel
  const handleCancel = useCallback(() => {
    setShowBuilder(false)
    setSelectedMetric(undefined)
  }, [])

  if (showBuilder) {
    return (
      <div className="container mx-auto py-6">
        <MetricBuilder
          metric={selectedMetric}
          onSave={handleMetricSave}
          onCancel={handleCancel}
        />
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Metric Workbench</h1>
          <p className="text-muted-foreground">
            Create, test, and manage custom evaluation metrics for your optimization tasks
          </p>
        </div>
        <Button onClick={handleNewMetric} disabled={loading}>
          <Plus className="mr-2 h-4 w-4" />
          New Metric
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>
            {error}
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={clearError}
              className="ml-2"
            >
              Dismiss
            </Button>
          </AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="library" className="flex items-center gap-2">
            <Library className="h-4 w-4" />
            My Metrics ({metrics.length})
          </TabsTrigger>
          <TabsTrigger value="templates" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Templates
          </TabsTrigger>
          <TabsTrigger value="builder" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            Builder
          </TabsTrigger>
        </TabsList>

        <TabsContent value="library" className="space-y-4">
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <Card key={i}>
                  <CardContent className="pt-6">
                    <div className="animate-pulse space-y-3">
                      <div className="h-4 bg-muted rounded w-3/4" />
                      <div className="h-3 bg-muted rounded w-full" />
                      <div className="h-3 bg-muted rounded w-2/3" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : metrics.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {metrics.map((metric) => (
                <Card key={metric.id} className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">{metric.name}</CardTitle>
                        <div className="flex items-center gap-2">
                          <Badge variant={metric.is_public ? 'default' : 'secondary'} className="text-xs">
                            {metric.is_public ? 'Public' : 'Private'}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {new Date(metric.updated_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <CardDescription className="mb-3 line-clamp-2">
                      {metric.description || 'No description provided'}
                    </CardDescription>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex flex-wrap gap-1">
                        {metric.tags?.slice(0, 2).map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {(metric.tags?.length || 0) > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{(metric.tags?.length || 0) - 2}
                          </Badge>
                        )}
                      </div>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleMetricSelect(metric)}
                        disabled={loading}
                      >
                        <Settings className="mr-2 h-4 w-4" />
                        Edit
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center text-muted-foreground">
                  <Code className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">No custom metrics yet</p>
                  <p className="text-sm mb-4">
                    Create your first custom metric to get started with advanced evaluation
                  </p>
                  <Button onClick={handleNewMetric}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Your First Metric
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Template Cards */}
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Beaker className="h-5 w-5" />
                  Basic Accuracy
                </CardTitle>
                <CardDescription>
                  Simple accuracy metric that compares predictions to ground truth
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex gap-1">
                    <Badge variant="outline" className="text-xs">Accuracy</Badge>
                    <Badge variant="outline" className="text-xs">Basic</Badge>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedMetric(undefined)
                      setShowBuilder(true)
                      setActiveTab('builder')
                    }}
                  >
                    Use Template
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Beaker className="h-5 w-5" />
                  Classification F1
                </CardTitle>
                <CardDescription>
                  F1 score metric for classification tasks with precision and recall
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex gap-1">
                    <Badge variant="outline" className="text-xs">Classification</Badge>
                    <Badge variant="outline" className="text-xs">F1 Score</Badge>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedMetric(undefined)
                      setShowBuilder(true)
                      setActiveTab('builder')
                    }}
                  >
                    Use Template
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Beaker className="h-5 w-5" />
                  Text Similarity
                </CardTitle>
                <CardDescription>
                  Text similarity metric using sequence matching and Jaccard similarity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex gap-1">
                    <Badge variant="outline" className="text-xs">Text</Badge>
                    <Badge variant="outline" className="text-xs">Similarity</Badge>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedMetric(undefined)
                      setShowBuilder(true)
                      setActiveTab('builder')
                    }}
                  >
                    Use Template
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="builder">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center text-muted-foreground">
                <Code className="mx-auto h-12 w-12 mb-4 opacity-50" />
                <p className="text-lg font-medium mb-2">Metric Builder</p>
                <p className="text-sm mb-4">
                  Create a new metric or select an existing one to edit
                </p>
                <div className="flex gap-2 justify-center">
                  <Button onClick={handleNewMetric}>
                    <Plus className="mr-2 h-4 w-4" />
                    New Metric
                  </Button>
                  <Button variant="outline" onClick={() => setActiveTab('library')}>
                    <Library className="mr-2 h-4 w-4" />
                    Browse Library
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default MetricWorkbench
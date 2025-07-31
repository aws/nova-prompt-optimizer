import { useState, useCallback, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Eye, 
  Code, 
  FileText, 
  AlertTriangle, 
  CheckCircle,
  Loader2,
  RefreshCw
} from 'lucide-react'
import { TemplateRenderer } from './TemplateRenderer'
import { usePrompt } from '@/hooks/usePrompt'
import { Prompt } from '@/types'
import { cn } from '@/lib/utils'

interface PromptPreviewProps {
  prompt: Prompt
  sampleData?: Record<string, any>
  onClose?: () => void
  className?: string
  showTemplateEditor?: boolean
  autoPreview?: boolean
}

export function PromptPreview({
  prompt,
  sampleData = {},
  onClose,
  className,
  showTemplateEditor = true,
  autoPreview = true,
}: PromptPreviewProps) {
  const { previewPrompt, preview } = usePrompt({ autoLoad: false })
  
  const [activeTab, setActiveTab] = useState<'preview' | 'template'>('preview')
  const [currentSampleData, setCurrentSampleData] = useState(sampleData)
  const [isLoading, setIsLoading] = useState(false)

  // Load preview on mount or when sample data changes
  useEffect(() => {
    if (autoPreview && Object.keys(currentSampleData).length > 0) {
      handlePreview()
    }
  }, [prompt.id, currentSampleData, autoPreview])

  // Handle preview generation
  const handlePreview = useCallback(async () => {
    if (!prompt.id) return
    
    setIsLoading(true)
    try {
      await previewPrompt(prompt.id, currentSampleData)
    } catch (error) {
      console.error('Preview failed:', error)
    } finally {
      setIsLoading(false)
    }
  }, [prompt.id, currentSampleData, previewPrompt])

  // Handle template rendering from TemplateRenderer
  const handleTemplateRender = useCallback((
    _renderedSystem: string, 
    _renderedUser: string, 
    variables: Record<string, any>
  ) => {
    setCurrentSampleData(variables)
  }, [])

  const previewData = preview.data
  const hasPreview = previewData !== null
  const hasErrors = preview.error !== null || (previewData?.validation_errors?.length || 0) > 0
  const isPreviewLoading = preview.loading === 'loading' || isLoading

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Prompt Preview
              <Badge variant="outline" className="text-xs">
                {prompt.name}
              </Badge>
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handlePreview}
                disabled={isPreviewLoading}
                className="flex items-center gap-1"
              >
                {isPreviewLoading ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <RefreshCw className="h-3 w-3" />
                )}
                Refresh
              </Button>
              {onClose && (
                <Button variant="outline" size="sm" onClick={onClose}>
                  Close
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Version: {prompt.version}</span>
            <span>Variables: {prompt.variables.length}</span>
            <span>System: {prompt.system_prompt.length} chars</span>
            <span>User: {prompt.user_prompt.length} chars</span>
          </div>
        </CardContent>
      </Card>

      {/* Content Tabs */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'preview' | 'template')}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="preview" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Live Preview
            {hasPreview && (
              <Badge variant="secondary" className="text-xs">
                Ready
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="template" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            Template Editor
            {prompt.variables.length > 0 && (
              <Badge variant="secondary" className="text-xs">
                {prompt.variables.length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Live Preview Tab */}
        <TabsContent value="preview" className="space-y-4">
          {isPreviewLoading && (
            <Card>
              <CardContent className="flex items-center justify-center py-8">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Generating preview...</span>
                </div>
              </CardContent>
            </Card>
          )}

          {hasErrors && !isPreviewLoading && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-1">
                  {preview.error && <div>{preview.error}</div>}
                  {previewData?.validation_errors?.map((error, index) => (
                    <div key={index}>{error}</div>
                  ))}
                </div>
              </AlertDescription>
            </Alert>
          )}

          {hasPreview && !hasErrors && !isPreviewLoading && (
            <div className="space-y-4">
              {/* Rendered System Prompt */}
              {previewData.rendered_system_prompt && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      System Prompt
                      <Badge variant="secondary" className="text-xs">
                        {previewData.rendered_system_prompt.length} chars
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-muted/30 rounded-md p-4 font-mono text-sm whitespace-pre-wrap">
                      {previewData.rendered_system_prompt}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Rendered User Prompt */}
              {previewData.rendered_user_prompt && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      User Prompt
                      <Badge variant="secondary" className="text-xs">
                        {previewData.rendered_user_prompt.length} chars
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-muted/30 rounded-md p-4 font-mono text-sm whitespace-pre-wrap">
                      {previewData.rendered_user_prompt}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Variables Used */}
              {previewData.variables_used && Object.keys(previewData.variables_used).length > 0 && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">Variables Used</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {Object.entries(previewData.variables_used).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between p-2 bg-muted/30 rounded">
                          <Badge variant="outline" className="text-xs">
                            {key}
                          </Badge>
                          <span className="text-sm text-muted-foreground truncate ml-2">
                            {String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {!hasPreview && !isPreviewLoading && !hasErrors && (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-8 text-center">
                <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No Preview Available</h3>
                <p className="text-muted-foreground mb-4">
                  Configure variables in the Template Editor tab to generate a preview.
                </p>
                <Button onClick={() => setActiveTab('template')}>
                  Configure Variables
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Template Editor Tab */}
        <TabsContent value="template" className="space-y-4">
          {showTemplateEditor && (
            <TemplateRenderer
              systemTemplate={prompt.system_prompt}
              userTemplate={prompt.user_prompt}
              variables={prompt.variables}
              sampleData={currentSampleData}
              onRender={handleTemplateRender}
              showPreview={true}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default PromptPreview
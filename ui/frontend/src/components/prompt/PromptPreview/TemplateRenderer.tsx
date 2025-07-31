import React, { useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle,
  Copy,
  Eye,
  EyeOff
} from 'lucide-react'
import { cn } from '@/lib/utils'

// interface TemplateVariable {
//   name: string
//   value: string
//   type?: 'text' | 'number' | 'boolean'
//   description?: string
//   required?: boolean
// }

interface TemplateRendererProps {
  systemTemplate: string
  userTemplate: string
  variables: string[]
  onRender?: (renderedSystem: string, renderedUser: string, variables: Record<string, any>) => void
  className?: string
  sampleData?: Record<string, any>
  showPreview?: boolean
}

// Simple template renderer (in production, you'd use a proper Jinja2 implementation)
function renderTemplate(template: string, variables: Record<string, any>): string {
  let rendered = template
  
  // Replace {{variable}} with values
  Object.entries(variables).forEach(([key, value]) => {
    const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g')
    rendered = rendered.replace(regex, String(value))
  })
  
  return rendered
}

// Extract variables from template
// function extractVariables(template: string): string[] {
//   const regex = /\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}/g
//   const matches = Array.from(template.matchAll(regex))
//   return [...new Set(matches.map(match => match[1]))]
// }

export function TemplateRenderer({
  systemTemplate,
  userTemplate,
  variables,
  onRender,
  className,
  sampleData = {},
  showPreview = true,
}: TemplateRendererProps) {
  const [variableValues, setVariableValues] = useState<Record<string, string>>(() => {
    const initial: Record<string, string> = {}
    variables.forEach(variable => {
      initial[variable] = sampleData[variable] || ''
    })
    return initial
  })
  
  const [renderedSystem, setRenderedSystem] = useState('')
  const [renderedUser, setRenderedUser] = useState('')
  const [renderErrors, setRenderErrors] = useState<string[]>([])
  const [isPreviewVisible, setIsPreviewVisible] = useState(showPreview)

  // Handle variable value change
  const handleVariableChange = useCallback((variable: string, value: string) => {
    setVariableValues(prev => ({
      ...prev,
      [variable]: value,
    }))
  }, [])

  // Render templates
  const handleRender = useCallback(() => {
    try {
      setRenderErrors([])
      
      const renderedSys = renderTemplate(systemTemplate, variableValues)
      const renderedUsr = renderTemplate(userTemplate, variableValues)
      
      setRenderedSystem(renderedSys)
      setRenderedUser(renderedUsr)
      
      onRender?.(renderedSys, renderedUsr, variableValues)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Rendering failed'
      setRenderErrors([errorMessage])
    }
  }, [systemTemplate, userTemplate, variableValues, onRender])

  // Auto-render when variables change
  React.useEffect(() => {
    if (Object.values(variableValues).some(v => v.trim() !== '')) {
      handleRender()
    }
  }, [variableValues, handleRender])

  // Copy rendered content
  const handleCopy = useCallback((content: string) => {
    navigator.clipboard.writeText(content)
  }, [])

  // Load sample data
  const handleLoadSample = useCallback(() => {
    const sampleValues: Record<string, string> = {}
    variables.forEach(variable => {
      // Generate sample values based on variable names
      if (variable.toLowerCase().includes('name')) {
        sampleValues[variable] = 'John Doe'
      } else if (variable.toLowerCase().includes('email')) {
        sampleValues[variable] = 'john.doe@example.com'
      } else if (variable.toLowerCase().includes('content')) {
        sampleValues[variable] = 'This is sample content for testing the template.'
      } else if (variable.toLowerCase().includes('date')) {
        sampleValues[variable] = new Date().toLocaleDateString()
      } else if (variable.toLowerCase().includes('number') || variable.toLowerCase().includes('count')) {
        sampleValues[variable] = '42'
      } else {
        sampleValues[variable] = `Sample ${variable}`
      }
    })
    setVariableValues(sampleValues)
  }, [variables])

  const hasVariables = variables.length > 0
  const hasValues = Object.values(variableValues).some(v => v.trim() !== '')
  const hasRendered = renderedSystem || renderedUser
  const hasErrors = renderErrors.length > 0

  return (
    <div className={cn('space-y-4', className)}>
      {/* Variables Input */}
      {hasVariables && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Template Variables</CardTitle>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLoadSample}
                  className="text-xs"
                >
                  Load Sample
                </Button>
                <Badge variant="secondary" className="text-xs">
                  {variables.length}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {variables.map((variable) => (
                <div key={variable} className="space-y-1">
                  <Label htmlFor={`var-${variable}`} className="text-sm">
                    {variable}
                  </Label>
                  <Input
                    id={`var-${variable}`}
                    placeholder={`Enter ${variable}...`}
                    value={variableValues[variable] || ''}
                    onChange={(e) => handleVariableChange(variable, e.target.value)}
                    className="text-sm"
                  />
                </div>
              ))}
            </div>
            
            <div className="flex items-center justify-between pt-2">
              <div className="text-xs text-muted-foreground">
                {hasValues ? 'Variables configured' : 'Enter values to see preview'}
              </div>
              <Button
                onClick={handleRender}
                disabled={!hasValues}
                size="sm"
                className="flex items-center gap-1"
              >
                <RefreshCw className="h-3 w-3" />
                Render
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Variables Message */}
      {!hasVariables && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            No variables detected in the templates. Add variables using {`{{variable_name}}`} syntax.
          </AlertDescription>
        </Alert>
      )}

      {/* Render Errors */}
      {hasErrors && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-1">
              {renderErrors.map((error, index) => (
                <div key={index}>{error}</div>
              ))}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Rendered Output */}
      {hasRendered && !hasErrors && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                Rendered Output
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsPreviewVisible(!isPreviewVisible)}
                className="flex items-center gap-1"
              >
                {isPreviewVisible ? (
                  <>
                    <EyeOff className="h-3 w-3" />
                    Hide
                  </>
                ) : (
                  <>
                    <Eye className="h-3 w-3" />
                    Show
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          
          {isPreviewVisible && (
            <CardContent className="space-y-4">
              {/* System Prompt Output */}
              {renderedSystem && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label className="text-sm font-medium">System Prompt</Label>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleCopy(renderedSystem)}
                      className="h-6 px-2 text-xs"
                    >
                      <Copy className="h-3 w-3 mr-1" />
                      Copy
                    </Button>
                  </div>
                  <div className="relative">
                    <Textarea
                      value={renderedSystem}
                      readOnly
                      className="min-h-[100px] bg-muted/30 font-mono text-sm resize-none"
                    />
                  </div>
                </div>
              )}

              {/* User Prompt Output */}
              {renderedUser && (
                <>
                  {renderedSystem && <Separator />}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label className="text-sm font-medium">User Prompt</Label>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleCopy(renderedUser)}
                        className="h-6 px-2 text-xs"
                      >
                        <Copy className="h-3 w-3 mr-1" />
                        Copy
                      </Button>
                    </div>
                    <div className="relative">
                      <Textarea
                        value={renderedUser}
                        readOnly
                        className="min-h-[100px] bg-muted/30 font-mono text-sm resize-none"
                      />
                    </div>
                  </div>
                </>
              )}

              {/* Statistics */}
              <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2 border-t">
                <span>System: {renderedSystem.length} chars</span>
                <span>User: {renderedUser.length} chars</span>
                <span>Total: {renderedSystem.length + renderedUser.length} chars</span>
              </div>
            </CardContent>
          )}
        </Card>
      )}
    </div>
  )
}

export default TemplateRenderer
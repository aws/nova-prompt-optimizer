import { useState, useCallback, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { 
  Save, 
  Eye, 
  FileText, 
  Copy, 
  AlertTriangle,
  CheckCircle,
  Loader2
} from 'lucide-react'
import { CodeEditor } from './CodeEditor'
import { VariableDetector } from './VariableDetector'
import { usePrompt } from '@/hooks/usePrompt'
import { Prompt, PromptCreateRequest, PromptUpdateRequest } from '@/types'
import { cn } from '@/lib/utils'

interface VariableInfo {
  name: string
  type: 'detected' | 'manual'
  description?: string
  defaultValue?: string
}

interface PromptEditorProps {
  prompt?: Prompt
  onSave?: (prompt: Prompt) => void
  onPreview?: (prompt: Prompt) => void
  onCancel?: () => void
  className?: string
  mode?: 'create' | 'edit'
  autoSave?: boolean
  showVersioning?: boolean
}

export function PromptEditor({
  prompt,
  onSave,
  onPreview,
  onCancel,
  className,
  mode = prompt ? 'edit' : 'create',
  showVersioning = true,
}: PromptEditorProps) {
  const { 
    createPrompt, 
    updatePrompt, 
    validatePrompt, 
    validation
  } = usePrompt({ autoLoad: false })

  // Form state
  const [name, setName] = useState(prompt?.name || '')
  const [description, setDescription] = useState(prompt?.description || '')
  const [systemPrompt, setSystemPrompt] = useState(prompt?.system_prompt || '')
  const [userPrompt, setUserPrompt] = useState(prompt?.user_prompt || '')
  const [variables, setVariables] = useState<VariableInfo[]>([])
  
  // UI state
  const [activeTab, setActiveTab] = useState<'system' | 'user'>('system')
  const [isSaving, setIsSaving] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [lastValidation, setLastValidation] = useState<Date | null>(null)

  // Validation debounce
  const [validationTimeout, setValidationTimeout] = useState<NodeJS.Timeout | null>(null)

  // Initialize variables from prompt
  useEffect(() => {
    if (prompt?.variables) {
      const initialVariables: VariableInfo[] = prompt.variables.map(name => ({
        name,
        type: 'detected' as const,
      }))
      setVariables(initialVariables)
    }
  }, [prompt])

  // Track unsaved changes
  useEffect(() => {
    if (prompt) {
      const hasChanges = 
        name !== prompt.name ||
        description !== (prompt.description || '') ||
        systemPrompt !== prompt.system_prompt ||
        userPrompt !== prompt.user_prompt
      setHasUnsavedChanges(hasChanges)
    } else {
      setHasUnsavedChanges(name.trim() !== '' || systemPrompt.trim() !== '' || userPrompt.trim() !== '')
    }
  }, [name, description, systemPrompt, userPrompt, prompt])

  // Debounced validation
  const debouncedValidation = useCallback(() => {
    if (validationTimeout) {
      clearTimeout(validationTimeout)
    }

    const timeout = setTimeout(async () => {
      if (systemPrompt.trim() || userPrompt.trim()) {
        setIsValidating(true)
        await validatePrompt(systemPrompt, userPrompt)
        setLastValidation(new Date())
        setIsValidating(false)
      }
    }, 500)

    setValidationTimeout(timeout)
  }, [systemPrompt, userPrompt, validatePrompt, validationTimeout])

  // Trigger validation on prompt changes
  useEffect(() => {
    debouncedValidation()
    return () => {
      if (validationTimeout) {
        clearTimeout(validationTimeout)
      }
    }
  }, [debouncedValidation])

  // Handle variable changes from CodeEditor
  const handleSystemVariablesChange = useCallback((detectedVars: string[]) => {
    setVariables(prev => {
      const manual = prev.filter(v => v.type === 'manual')
      const detected = detectedVars.map(name => ({
        name,
        type: 'detected' as const,
      }))
      return [...detected, ...manual]
    })
  }, [])

  const handleUserVariablesChange = useCallback((detectedVars: string[]) => {
    setVariables(prev => {
      const manual = prev.filter(v => v.type === 'manual')
      const systemDetected = prev.filter(v => v.type === 'detected')
      
      // Merge with user-detected variables
      const allDetected = new Set([
        ...systemDetected.map(v => v.name),
        ...detectedVars
      ])
      
      const detected = Array.from(allDetected).map(name => ({
        name,
        type: 'detected' as const,
      }))
      
      return [...detected, ...manual]
    })
  }, [])

  // Handle save
  const handleSave = useCallback(async () => {
    if (!name.trim()) {
      return
    }

    setIsSaving(true)
    try {
      const promptData = {
        name: name.trim(),
        description: description.trim() || undefined,
        system_prompt: systemPrompt,
        user_prompt: userPrompt,
      }

      let savedPrompt: Prompt
      if (mode === 'edit' && prompt) {
        savedPrompt = await updatePrompt(prompt.id, promptData as PromptUpdateRequest)
      } else {
        savedPrompt = await createPrompt(promptData as PromptCreateRequest)
      }

      setHasUnsavedChanges(false)
      onSave?.(savedPrompt)
    } catch (error) {
      console.error('Failed to save prompt:', error)
    } finally {
      setIsSaving(false)
    }
  }, [name, description, systemPrompt, userPrompt, mode, prompt, updatePrompt, createPrompt, onSave])

  // Handle preview
  const handlePreview = useCallback(() => {
    if (prompt || (name.trim() && (systemPrompt.trim() || userPrompt.trim()))) {
      const previewPrompt: Prompt = prompt || {
        id: 'preview',
        name: name.trim(),
        description: description.trim(),
        system_prompt: systemPrompt,
        user_prompt: userPrompt,
        variables: variables.map(v => v.name),
        version: 1,
        is_template: true,
        metadata: {},
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      onPreview?.(previewPrompt)
    }
  }, [prompt, name, description, systemPrompt, userPrompt, variables, onPreview])

  // Handle duplicate (for edit mode)
  const handleDuplicate = useCallback(() => {
    if (prompt) {
      setName(`${prompt.name} (Copy)`)
      setHasUnsavedChanges(true)
    }
  }, [prompt])

  const canSave = name.trim() !== '' && (systemPrompt.trim() !== '' || userPrompt.trim() !== '')
  const canPreview = canSave
  const validationErrors = validation.data?.errors || []
  const validationWarnings = validation.data?.warnings || []
  const isValid = validation.data?.is_valid !== false

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + S to save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        if (canSave && !isSaving) {
          handleSave()
        }
      }
      
      // Ctrl/Cmd + P to preview
      if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault()
        if (canPreview) {
          handlePreview()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [canSave, canPreview, isSaving, handleSave, handlePreview])

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              {mode === 'edit' ? 'Edit Prompt' : 'Create New Prompt'}
              {hasUnsavedChanges && (
                <Badge variant="outline" className="text-xs">
                  Unsaved Changes
                </Badge>
              )}
            </CardTitle>
            {showVersioning && prompt && (
              <Badge variant="secondary">
                Version {prompt.version}
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="prompt-name">Prompt Name *</Label>
              <Input
                id="prompt-name"
                placeholder="Enter prompt name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className={!name.trim() && hasUnsavedChanges ? 'border-destructive' : ''}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="prompt-description">Description</Label>
              <Input
                id="prompt-description"
                placeholder="Brief description (optional)"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>

          {/* Validation Status */}
          {(isValidating || lastValidation) && (
            <div className="flex items-center gap-2 text-sm">
              {isValidating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-muted-foreground">Validating template...</span>
                </>
              ) : isValid ? (
                <>
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-green-600">Template is valid</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="h-4 w-4 text-destructive" />
                  <span className="text-destructive">Template has errors</span>
                </>
              )}
              {lastValidation && (
                <span className="text-xs text-muted-foreground ml-auto">
                  Last checked: {lastValidation.toLocaleTimeString()}
                </span>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Prompt Editors */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Prompt Templates</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'system' | 'user')}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="system" className="flex items-center gap-2">
                    System Prompt
                    {systemPrompt.trim() && (
                      <Badge variant="secondary" className="text-xs">
                        {systemPrompt.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="user" className="flex items-center gap-2">
                    User Prompt
                    {userPrompt.trim() && (
                      <Badge variant="secondary" className="text-xs">
                        {userPrompt.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="system" className="mt-4">
                  <CodeEditor
                    value={systemPrompt}
                    onChange={setSystemPrompt}
                    placeholder="Enter your system prompt template here...&#10;&#10;Use {{variable_name}} for dynamic content.&#10;&#10;Example:&#10;You are a helpful assistant that analyzes {{content_type}}.&#10;Please provide {{analysis_depth}} analysis."
                    label="System Prompt"
                    errors={validationErrors.filter(e => e.includes('system'))}
                    warnings={validationWarnings.filter(w => w.includes('system'))}
                    onVariablesChange={handleSystemVariablesChange}
                  />
                </TabsContent>

                <TabsContent value="user" className="mt-4">
                  <CodeEditor
                    value={userPrompt}
                    onChange={setUserPrompt}
                    placeholder="Enter your user prompt template here...&#10;&#10;Use {{variable_name}} for dynamic content.&#10;&#10;Example:&#10;Please analyze the following {{content_type}}:&#10;&#10;{{content}}&#10;&#10;Focus on: {{focus_areas}}"
                    label="User Prompt"
                    errors={validationErrors.filter(e => e.includes('user'))}
                    warnings={validationWarnings.filter(w => w.includes('user'))}
                    onVariablesChange={handleUserVariablesChange}
                  />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Variables Panel */}
        <div>
          <VariableDetector
            variables={variables}
            onVariablesChange={setVariables}
            showAddVariable={true}
            showVariableDetails={true}
          />
        </div>
      </div>

      {/* Actions */}
      <Card>
        <CardFooter className="flex items-center justify-between pt-6">
          <div className="flex items-center gap-2">
            {mode === 'edit' && (
              <Button
                variant="outline"
                onClick={handleDuplicate}
                className="flex items-center gap-2"
              >
                <Copy className="h-4 w-4" />
                Duplicate
              </Button>
            )}
          </div>

          <div className="flex items-center gap-2">
            {onCancel && (
              <Button variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            )}
            <Button
              variant="outline"
              onClick={handlePreview}
              disabled={!canPreview}
              className="flex items-center gap-2"
            >
              <Eye className="h-4 w-4" />
              Preview
            </Button>
            <Button
              onClick={handleSave}
              disabled={!canSave || isSaving}
              className="flex items-center gap-2"
            >
              {isSaving ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              {mode === 'edit' ? 'Update' : 'Save'} Prompt
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}

export default PromptEditor
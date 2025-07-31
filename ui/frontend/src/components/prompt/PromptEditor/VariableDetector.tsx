import React from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Plus, X, Variable } from 'lucide-react'
import { cn } from '@/lib/utils'

interface VariableInfo {
  name: string
  type: 'detected' | 'manual'
  description?: string
  defaultValue?: string
}

interface VariableDetectorProps {
  variables: VariableInfo[]
  onVariablesChange: (variables: VariableInfo[]) => void
  className?: string
  showAddVariable?: boolean
  showVariableDetails?: boolean
}

export function VariableDetector({
  variables,
  onVariablesChange,
  className,
  showAddVariable = true,
  showVariableDetails = true,
}: VariableDetectorProps) {
  const [newVariableName, setNewVariableName] = React.useState('')
  const [newVariableDescription, setNewVariableDescription] = React.useState('')

  const detectedVariables = variables.filter(v => v.type === 'detected')
  const manualVariables = variables.filter(v => v.type === 'manual')

  const handleAddVariable = () => {
    if (!newVariableName.trim()) return

    const newVariable: VariableInfo = {
      name: newVariableName.trim(),
      type: 'manual',
      description: newVariableDescription.trim() || undefined,
    }

    // Check if variable already exists
    const exists = variables.some(v => v.name === newVariable.name)
    if (exists) return

    onVariablesChange([...variables, newVariable])
    setNewVariableName('')
    setNewVariableDescription('')
  }

  const handleRemoveVariable = (name: string) => {
    onVariablesChange(variables.filter(v => v.name !== name))
  }

  // const handleUpdateVariable = (name: string, updates: Partial<VariableInfo>) => {
  //   onVariablesChange(
  //     variables.map(v => 
  //       v.name === name ? { ...v, ...updates } : v
  //     )
  //   )
  // }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddVariable()
    }
  }

  if (variables.length === 0 && !showAddVariable) {
    return (
      <div className={cn('text-center py-8 text-muted-foreground', className)}>
        <Variable className="mx-auto h-12 w-12 mb-2 opacity-50" />
        <p className="text-sm">No variables detected</p>
        <p className="text-xs">Use {`{{variable_name}}`} syntax in your prompts</p>
      </div>
    )
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Variable className="h-4 w-4" />
          Template Variables
          <Badge variant="secondary" className="ml-auto">
            {variables.length}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Detected Variables */}
        {detectedVariables.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-medium text-green-600 dark:text-green-400">
                Auto-detected
              </h4>
              <Badge variant="outline" className="text-xs">
                {detectedVariables.length}
              </Badge>
            </div>
            <div className="flex flex-wrap gap-2">
              {detectedVariables.map((variable) => (
                <Badge
                  key={variable.name}
                  variant="secondary"
                  className="bg-green-50 text-green-700 border-green-200 dark:bg-green-950/20 dark:text-green-300 dark:border-green-800"
                >
                  {variable.name}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Manual Variables */}
        {manualVariables.length > 0 && (
          <>
            {detectedVariables.length > 0 && <Separator />}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-medium text-blue-600 dark:text-blue-400">
                  Manual
                </h4>
                <Badge variant="outline" className="text-xs">
                  {manualVariables.length}
                </Badge>
              </div>
              <div className="space-y-2">
                {manualVariables.map((variable) => (
                  <div
                    key={variable.name}
                    className="flex items-center justify-between p-2 rounded-md border bg-muted/30"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Badge
                          variant="secondary"
                          className="bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/20 dark:text-blue-300 dark:border-blue-800"
                        >
                          {variable.name}
                        </Badge>
                      </div>
                      {showVariableDetails && variable.description && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {variable.description}
                        </p>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveVariable(variable.name)}
                      className="h-6 w-6 p-0 text-muted-foreground hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Add Variable Form */}
        {showAddVariable && (
          <>
            {variables.length > 0 && <Separator />}
            <div className="space-y-3">
              <h4 className="text-sm font-medium">Add Variable</h4>
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <Label htmlFor="variable-name" className="text-xs">
                    Variable Name
                  </Label>
                  <Input
                    id="variable-name"
                    placeholder="variable_name"
                    value={newVariableName}
                    onChange={(e) => setNewVariableName(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="h-8 text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="variable-description" className="text-xs">
                    Description (optional)
                  </Label>
                  <Input
                    id="variable-description"
                    placeholder="Brief description"
                    value={newVariableDescription}
                    onChange={(e) => setNewVariableDescription(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="h-8 text-sm"
                  />
                </div>
              </div>
              <Button
                onClick={handleAddVariable}
                disabled={!newVariableName.trim()}
                size="sm"
                className="w-full h-8"
              >
                <Plus className="h-3 w-3 mr-1" />
                Add Variable
              </Button>
            </div>
          </>
        )}

        {/* Usage hint */}
        {variables.length === 0 && (
          <div className="text-center py-4 text-muted-foreground">
            <Variable className="mx-auto h-8 w-8 mb-2 opacity-50" />
            <p className="text-sm">No variables detected</p>
            <p className="text-xs">Use {`{{variable_name}}`} syntax in your prompts</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default VariableDetector
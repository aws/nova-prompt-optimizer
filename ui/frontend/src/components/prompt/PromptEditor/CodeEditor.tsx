import React, { useCallback, useEffect, useRef, useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertTriangle, CheckCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface CodeEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  label?: string
  className?: string
  disabled?: boolean
  errors?: string[]
  warnings?: string[]
  onVariablesChange?: (variables: string[]) => void
}

// Simple Jinja2 variable detection regex
const JINJA_VARIABLE_REGEX = /\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}/g

// Validation patterns for common Jinja2 syntax errors
const VALIDATION_PATTERNS = {
  unclosedBraces: /\{\{[^}]*$/,
  unopenedBraces: /^[^{]*\}\}/,
  invalidVariableName: /\{\{\s*[^a-zA-Z_][^}]*\}\}/,
  extraSpaces: /\{\{\s{2,}|\s{2,}\}\}/,
}

export function CodeEditor({
  value,
  onChange,
  placeholder = 'Enter your prompt template...',
  label,
  className,
  disabled = false,
  errors = [],
  warnings = [],
  onVariablesChange,
}: CodeEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const [detectedVariables, setDetectedVariables] = useState<string[]>([])

  // Detect variables and validate syntax
  const detectVariables = useCallback((text: string) => {
    const matches = Array.from(text.matchAll(JINJA_VARIABLE_REGEX))
    const vars = [...new Set(matches.map(match => match[1]))]
    setDetectedVariables(vars)
    onVariablesChange?.(vars)
  }, [onVariablesChange])

  // Validate template syntax
  const validateSyntax = useCallback((text: string): { errors: string[], warnings: string[] } => {
    const errors: string[] = []
    const warnings: string[] = []

    // Check for unclosed braces
    if (VALIDATION_PATTERNS.unclosedBraces.test(text)) {
      errors.push('Unclosed template variable - missing }}}')
    }

    // Check for unopened braces
    if (VALIDATION_PATTERNS.unopenedBraces.test(text)) {
      errors.push('Unopened template variable - missing {{')
    }

    // Check for invalid variable names
    if (VALIDATION_PATTERNS.invalidVariableName.test(text)) {
      errors.push('Invalid variable name - must start with letter or underscore')
    }

    // Check for extra spaces (warning only)
    if (VALIDATION_PATTERNS.extraSpaces.test(text)) {
      warnings.push('Extra spaces in template variables - consider cleaning up')
    }

    return { errors, warnings }
  }, [])

  // Handle text change
  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    onChange(newValue)
    detectVariables(newValue)
    
    // Perform client-side validation
    // const validation = validateSyntax(newValue)
    // Note: In a real implementation, you might want to emit these validation results
    // to the parent component for display
  }, [onChange, detectVariables, validateSyntax])

  // Auto-resize textarea
  const autoResize = useCallback(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.max(textarea.scrollHeight, 120)}px`
    }
  }, [])

  // Detect variables on value change
  useEffect(() => {
    detectVariables(value)
  }, [value, detectVariables])

  // Auto-resize on value change
  useEffect(() => {
    autoResize()
  }, [value, autoResize])

  const hasErrors = errors.length > 0
  const hasWarnings = warnings.length > 0
  const hasVariables = detectedVariables.length > 0

  return (
    <div className={cn('space-y-2', className)}>
      {label && (
        <div className="flex items-center justify-between">
          <Label htmlFor={`code-editor-${label}`} className="text-sm font-medium">
            {label}
          </Label>
          {hasVariables && (
            <div className="flex items-center gap-1">
              <span className="text-xs text-muted-foreground">Variables:</span>
              <div className="flex flex-wrap gap-1">
                {detectedVariables.slice(0, 3).map((variable) => (
                  <Badge key={variable} variant="secondary" className="text-xs">
                    {variable}
                  </Badge>
                ))}
                {detectedVariables.length > 3 && (
                  <Badge variant="secondary" className="text-xs">
                    +{detectedVariables.length - 3}
                  </Badge>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="relative">
        <Textarea
          ref={textareaRef}
          id={`code-editor-${label}`}
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          disabled={disabled}
          className={cn(
            'min-h-[120px] font-mono text-sm resize-none',
            'focus:ring-2 focus:ring-primary/20',
            hasErrors && 'border-destructive focus:ring-destructive/20',
            hasWarnings && !hasErrors && 'border-yellow-500 focus:ring-yellow-500/20'
          )}
          style={{ height: 'auto' }}
        />

        {/* Syntax highlighting overlay could be added here in the future */}
      </div>

      {/* Error messages */}
      {hasErrors && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-1">
              {errors.map((error, index) => (
                <div key={index} className="text-sm">
                  {error}
                </div>
              ))}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Warning messages */}
      {hasWarnings && !hasErrors && (
        <Alert className="border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20">
          <AlertTriangle className="h-4 w-4 text-yellow-600" />
          <AlertDescription>
            <div className="space-y-1">
              {warnings.map((warning, index) => (
                <div key={index} className="text-sm text-yellow-700 dark:text-yellow-300">
                  {warning}
                </div>
              ))}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Success state when no errors/warnings */}
      {!hasErrors && !hasWarnings && value.trim() && (
        <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
          <CheckCircle className="h-4 w-4" />
          <span>Template syntax is valid</span>
        </div>
      )}

      {/* Variable summary */}
      {hasVariables && (
        <div className="text-xs text-muted-foreground">
          {detectedVariables.length} variable{detectedVariables.length !== 1 ? 's' : ''} detected: {detectedVariables.join(', ')}
        </div>
      )}
    </div>
  )
}

export default CodeEditor
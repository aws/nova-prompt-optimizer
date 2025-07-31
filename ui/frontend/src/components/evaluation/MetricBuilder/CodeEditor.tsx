import React, { useCallback, useEffect, useRef, useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { AlertTriangle, CheckCircle, Copy } from 'lucide-react'
import { cn } from '@/lib/utils'

interface CodeEditorProps {
  value: string
  onChange: (value: string) => void
  language?: 'python' | 'javascript' | 'json'
  placeholder?: string
  label?: string
  className?: string
  disabled?: boolean
  errors?: string[]
  warnings?: string[]
  minHeight?: string
  maxHeight?: string
  showLineNumbers?: boolean
  onValidate?: (code: string) => void
}

// Python syntax patterns for basic highlighting
const PYTHON_PATTERNS = {
  keywords: /\b(class|def|if|else|elif|for|while|try|except|finally|import|from|as|return|yield|lambda|with|async|await|pass|break|continue|global|nonlocal|assert|del|raise|True|False|None|and|or|not|in|is)\b/g,
  strings: /(["'])((?:\\.|(?!\1)[^\\])*?)\1/g,
  comments: /#.*$/gm,
  numbers: /\b\d+\.?\d*\b/g,
  functions: /\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()/g,
  decorators: /@[a-zA-Z_][a-zA-Z0-9_.]*/g,
  operators: /[+\-*/%=<>!&|^~]/g,
  brackets: /[()[\]{}]/g
}

// Python validation patterns
const PYTHON_VALIDATION = {
  indentationError: /^[ \t]*\S/gm,
  unclosedString: /["'](?:[^"'\\]|\\.)*$/gm,
  unclosedParens: /\([^)]*$/gm,
  unclosedBrackets: /\[[^\]]*$/gm,
  unclosedBraces: /\{[^}]*$/gm,
  invalidIndentation: /^([ ]*\t+[ ]*|\t*[ ]+\t*)/gm
}

export function CodeEditor({
  value,
  onChange,
  language = 'python',
  placeholder = 'Enter your code...',
  label,
  className,
  disabled = false,
  errors = [],
  warnings = [],
  minHeight = '200px',
  maxHeight = '600px',
  showLineNumbers = true,
  onValidate,
}: CodeEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const highlightRef = useRef<HTMLDivElement>(null)
  const [localErrors, setLocalErrors] = useState<string[]>([])
  const [localWarnings, setLocalWarnings] = useState<string[]>([])
  const [lineCount, setLineCount] = useState(1)

  // Basic Python syntax validation
  const validatePython = useCallback((code: string) => {
    const errors: string[] = []
    const warnings: string[] = []

    if (!code.trim()) {
      return { errors, warnings }
    }

    // Check for unclosed strings
    const unclosedStrings = code.match(PYTHON_VALIDATION.unclosedString)
    if (unclosedStrings) {
      errors.push('Unclosed string literal detected')
    }

    // Check for unclosed parentheses
    const openParens = (code.match(/\(/g) || []).length
    const closeParens = (code.match(/\)/g) || []).length
    if (openParens !== closeParens) {
      errors.push(`Mismatched parentheses: ${openParens} open, ${closeParens} close`)
    }

    // Check for unclosed brackets
    const openBrackets = (code.match(/\[/g) || []).length
    const closeBrackets = (code.match(/\]/g) || []).length
    if (openBrackets !== closeBrackets) {
      errors.push(`Mismatched brackets: ${openBrackets} open, ${closeBrackets} close`)
    }

    // Check for unclosed braces
    const openBraces = (code.match(/\{/g) || []).length
    const closeBraces = (code.match(/\}/g) || []).length
    if (openBraces !== closeBraces) {
      errors.push(`Mismatched braces: ${openBraces} open, ${closeBraces} close`)
    }

    // Check for mixed indentation (warning)
    if (PYTHON_VALIDATION.invalidIndentation.test(code)) {
      warnings.push('Mixed tabs and spaces detected - use consistent indentation')
    }

    // Check for required methods in metric classes
    if (code.includes('class') && !code.includes('def apply(')) {
      warnings.push('Metric class should implement an apply() method')
    }

    if (code.includes('class') && !code.includes('def batch_apply(')) {
      warnings.push('Metric class should implement a batch_apply() method')
    }

    return { errors, warnings }
  }, [])

  // Apply syntax highlighting
  const applySyntaxHighlighting = useCallback((code: string) => {
    if (language !== 'python') return code

    let highlighted = code
      // Escape HTML
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')

    // Apply highlighting patterns
    highlighted = highlighted
      .replace(PYTHON_PATTERNS.comments, '<span class="text-green-600 dark:text-green-400">$&</span>')
      .replace(PYTHON_PATTERNS.strings, '<span class="text-amber-600 dark:text-amber-400">$&</span>')
      .replace(PYTHON_PATTERNS.keywords, '<span class="text-blue-600 dark:text-blue-400 font-semibold">$&</span>')
      .replace(PYTHON_PATTERNS.decorators, '<span class="text-purple-600 dark:text-purple-400">$&</span>')
      .replace(PYTHON_PATTERNS.numbers, '<span class="text-orange-600 dark:text-orange-400">$&</span>')
      .replace(PYTHON_PATTERNS.functions, '<span class="text-cyan-600 dark:text-cyan-400">$1</span>')

    return highlighted
  }, [language])

  // Handle text change
  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    onChange(newValue)

    // Update line count
    const lines = newValue.split('\n').length
    setLineCount(lines)

    // Validate code
    if (language === 'python') {
      const validation = validatePython(newValue)
      setLocalErrors(validation.errors)
      setLocalWarnings(validation.warnings)
      onValidate?.(newValue)
    }
  }, [onChange, language, validatePython, onValidate])

  // Handle scroll synchronization
  const handleScroll = useCallback(() => {
    if (textareaRef.current && highlightRef.current) {
      highlightRef.current.scrollTop = textareaRef.current.scrollTop
      highlightRef.current.scrollLeft = textareaRef.current.scrollLeft
    }
  }, [])

  // Handle tab key for proper indentation
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault()
      const textarea = e.currentTarget
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const newValue = value.substring(0, start) + '    ' + value.substring(end)
      onChange(newValue)
      
      // Set cursor position after the inserted spaces
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4
      }, 0)
    }
  }, [value, onChange])

  // Copy code to clipboard
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(value)
    } catch (error) {
      // Fallback for older browsers
      const textarea = document.createElement('textarea')
      textarea.value = value
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
  }, [value])

  // Update syntax highlighting when value changes
  useEffect(() => {
    if (highlightRef.current) {
      highlightRef.current.innerHTML = applySyntaxHighlighting(value)
    }
  }, [value, applySyntaxHighlighting])

  // Update line count when value changes
  useEffect(() => {
    const lines = value.split('\n').length
    setLineCount(lines)
  }, [value])

  const allErrors = [...errors, ...localErrors]
  const allWarnings = [...warnings, ...localWarnings]
  const hasErrors = allErrors.length > 0
  const hasWarnings = allWarnings.length > 0

  return (
    <div className={cn('space-y-2', className)}>
      {label && (
        <div className="flex items-center justify-between">
          <Label htmlFor={`code-editor-${label}`} className="text-sm font-medium">
            {label}
          </Label>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {language}
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              disabled={!value.trim()}
              className="h-6 px-2"
            >
              <Copy className="h-3 w-3" />
            </Button>
          </div>
        </div>
      )}

      <div className="relative border rounded-md overflow-hidden">
        {/* Line numbers */}
        {showLineNumbers && (
          <div className="absolute left-0 top-0 bottom-0 w-12 bg-muted/50 border-r flex flex-col text-xs text-muted-foreground font-mono leading-6 pt-3 pl-2 select-none z-10">
            {Array.from({ length: lineCount }, (_, i) => (
              <div key={i + 1} className="h-6 flex items-center">
                {i + 1}
              </div>
            ))}
          </div>
        )}

        {/* Syntax highlighting overlay */}
        <div
          ref={highlightRef}
          className={cn(
            'absolute inset-0 font-mono text-sm leading-6 p-3 pointer-events-none overflow-auto whitespace-pre-wrap break-words',
            showLineNumbers && 'pl-16'
          )}
          style={{
            minHeight,
            maxHeight,
            color: 'transparent'
          }}
          aria-hidden="true"
        />

        {/* Actual textarea */}
        <Textarea
          ref={textareaRef}
          id={`code-editor-${label}`}
          value={value}
          onChange={handleChange}
          onScroll={handleScroll}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className={cn(
            'relative bg-transparent font-mono text-sm leading-6 resize-none border-0 focus:ring-0',
            showLineNumbers && 'pl-16',
            hasErrors && 'border-destructive',
            hasWarnings && !hasErrors && 'border-yellow-500'
          )}
          style={{
            minHeight,
            maxHeight,
            caretColor: 'currentColor'
          }}
        />
      </div>

      {/* Error messages */}
      {hasErrors && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-1">
              {allErrors.map((error, index) => (
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
              {allWarnings.map((warning, index) => (
                <div key={index} className="text-sm text-yellow-700 dark:text-yellow-300">
                  {warning}
                </div>
              ))}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Success state */}
      {!hasErrors && !hasWarnings && value.trim() && language === 'python' && (
        <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
          <CheckCircle className="h-4 w-4" />
          <span>Code syntax looks good</span>
        </div>
      )}

      {/* Code stats */}
      {value.trim() && (
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span>{lineCount} lines</span>
          <span>{value.length} characters</span>
          <span>{value.split(/\s+/).filter(Boolean).length} words</span>
        </div>
      )}
    </div>
  )
}

export default CodeEditor
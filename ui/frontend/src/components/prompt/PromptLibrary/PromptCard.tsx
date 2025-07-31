// import React from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { 
  FileText, 
  MoreVertical, 
  Edit, 
  Copy, 
  Download, 
  Trash2, 
  Eye,
  Calendar,
  Variable
} from 'lucide-react'
import { Prompt } from '@/types'
import { cn } from '@/lib/utils'

interface PromptCardProps {
  prompt: Prompt
  onSelect?: (prompt: Prompt) => void
  onEdit?: (prompt: Prompt) => void
  onDuplicate?: (prompt: Prompt) => void
  onDelete?: (prompt: Prompt) => void
  onPreview?: (prompt: Prompt) => void
  onExport?: (prompt: Prompt) => void
  className?: string
  selected?: boolean
  showActions?: boolean
}

export function PromptCard({
  prompt,
  onSelect,
  onEdit,
  onDuplicate,
  onDelete,
  onPreview,
  onExport,
  className,
  selected = false,
  showActions = true,
}: PromptCardProps) {
  const handleCardClick = () => {
    onSelect?.(prompt)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const getTotalLength = () => {
    return prompt.system_prompt.length + prompt.user_prompt.length
  }

  return (
    <Card 
      className={cn(
        'cursor-pointer transition-all duration-200 hover:shadow-md',
        selected && 'ring-2 ring-primary ring-offset-2',
        className
      )}
      onClick={handleCardClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-base flex items-center gap-2 truncate">
              <FileText className="h-4 w-4 flex-shrink-0" />
              <span className="truncate">{prompt.name}</span>
            </CardTitle>
            {prompt.description && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                {prompt.description}
              </p>
            )}
          </div>
          
          {showActions && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {onPreview && (
                  <DropdownMenuItem onClick={(e) => {
                    e.stopPropagation()
                    onPreview(prompt)
                  }}>
                    <Eye className="h-4 w-4 mr-2" />
                    Preview
                  </DropdownMenuItem>
                )}
                {onEdit && (
                  <DropdownMenuItem onClick={(e) => {
                    e.stopPropagation()
                    onEdit(prompt)
                  }}>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </DropdownMenuItem>
                )}
                {onDuplicate && (
                  <DropdownMenuItem onClick={(e) => {
                    e.stopPropagation()
                    onDuplicate(prompt)
                  }}>
                    <Copy className="h-4 w-4 mr-2" />
                    Duplicate
                  </DropdownMenuItem>
                )}
                {onExport && (
                  <DropdownMenuItem onClick={(e) => {
                    e.stopPropagation()
                    onExport(prompt)
                  }}>
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </DropdownMenuItem>
                )}
                {(onEdit || onDuplicate || onExport) && onDelete && (
                  <DropdownMenuSeparator />
                )}
                {onDelete && (
                  <DropdownMenuItem 
                    onClick={(e) => {
                      e.stopPropagation()
                      onDelete(prompt)
                    }}
                    className="text-destructive focus:text-destructive"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </CardHeader>

      <CardContent className="pb-3">
        <div className="space-y-3">
          {/* Metrics */}
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <Variable className="h-3 w-3" />
              <span>{prompt.variables.length} vars</span>
            </div>
            <div className="flex items-center gap-1">
              <FileText className="h-3 w-3" />
              <span>{getTotalLength()} chars</span>
            </div>
            <div className="flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              <span>v{prompt.version}</span>
            </div>
          </div>

          {/* Variables Preview */}
          {prompt.variables.length > 0 && (
            <div className="space-y-1">
              <div className="text-xs font-medium text-muted-foreground">Variables:</div>
              <div className="flex flex-wrap gap-1">
                {prompt.variables.slice(0, 4).map((variable) => (
                  <Badge key={variable} variant="secondary" className="text-xs">
                    {variable}
                  </Badge>
                ))}
                {prompt.variables.length > 4 && (
                  <Badge variant="secondary" className="text-xs">
                    +{prompt.variables.length - 4}
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Template Preview */}
          <div className="space-y-2">
            {prompt.system_prompt && (
              <div className="space-y-1">
                <div className="text-xs font-medium text-muted-foreground">System:</div>
                <div className="text-xs bg-muted/30 rounded p-2 font-mono line-clamp-2">
                  {prompt.system_prompt}
                </div>
              </div>
            )}
            {prompt.user_prompt && (
              <div className="space-y-1">
                <div className="text-xs font-medium text-muted-foreground">User:</div>
                <div className="text-xs bg-muted/30 rounded p-2 font-mono line-clamp-2">
                  {prompt.user_prompt}
                </div>
              </div>
            )}
          </div>
        </div>
      </CardContent>

      <CardFooter className="pt-0">
        <div className="flex items-center justify-between w-full text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            {prompt.is_template && (
              <Badge variant="outline" className="text-xs">
                Template
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            <span>Updated {formatDate(prompt.updated_at)}</span>
          </div>
        </div>
      </CardFooter>
    </Card>
  )
}

export default PromptCard
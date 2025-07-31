import { useState, useCallback, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Library, 
  Search, 
  Plus, 
  SortAsc, 
  SortDesc,
  Grid,
  List,
  Loader2,
  AlertTriangle,
  FileText
} from 'lucide-react'
import { PromptCard } from './PromptCard'
import { usePrompt } from '@/hooks/usePrompt'
import { Prompt } from '@/types'
import { cn } from '@/lib/utils'

interface PromptLibraryProps {
  onSelect?: (prompt: Prompt) => void
  onEdit?: (prompt: Prompt) => void
  onPreview?: (prompt: Prompt) => void
  onCreate?: () => void
  className?: string
  selectedPrompt?: Prompt
  showActions?: boolean
  viewMode?: 'grid' | 'list'
}

type SortOption = 'name' | 'updated' | 'created' | 'variables'
type SortDirection = 'asc' | 'desc'

export function PromptLibrary({
  onSelect,
  onEdit,
  onPreview,
  onCreate,
  className,
  selectedPrompt,
  showActions = true,
  viewMode: initialViewMode = 'grid',
}: PromptLibraryProps) {
  const { 
    prompts, 
    library,
    deletePrompt, 
    duplicatePrompt, 
    exportPrompt,
    loadPrompts,
    isLoading 
  } = usePrompt()

  // UI State
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<SortOption>('updated')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(initialViewMode)
  const [selectedCategory] = useState<string>('all')
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [promptToDelete, setPromptToDelete] = useState<Prompt | null>(null)

  // Filter and sort prompts
  const filteredAndSortedPrompts = useMemo(() => {
    if (!prompts.data?.items) return []

    let filtered = prompts.data.items

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(prompt => 
        prompt.name.toLowerCase().includes(query) ||
        prompt.description?.toLowerCase().includes(query) ||
        prompt.variables.some(v => v.toLowerCase().includes(query))
      )
    }

    // Filter by category (if categories are available)
    if (selectedCategory !== 'all' && library.data?.categories) {
      // This would need to be implemented based on how categories are stored
      // For now, we'll skip category filtering
    }

    // Sort prompts
    const sorted = [...filtered].sort((a, b) => {
      let comparison = 0
      
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'updated':
          comparison = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime()
          break
        case 'created':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          break
        case 'variables':
          comparison = a.variables.length - b.variables.length
          break
        default:
          comparison = 0
      }

      return sortDirection === 'desc' ? -comparison : comparison
    })

    return sorted
  }, [prompts.data?.items, searchQuery, sortBy, sortDirection, selectedCategory, library.data?.categories])

  // Handle prompt actions
  const handleDelete = useCallback((prompt: Prompt) => {
    setPromptToDelete(prompt)
    setDeleteDialogOpen(true)
  }, [])

  const confirmDelete = useCallback(async () => {
    if (promptToDelete) {
      await deletePrompt(promptToDelete.id)
      setDeleteDialogOpen(false)
      setPromptToDelete(null)
    }
  }, [promptToDelete, deletePrompt])

  const handleDuplicate = useCallback(async (prompt: Prompt) => {
    await duplicatePrompt(prompt.id, `${prompt.name} (Copy)`)
  }, [duplicatePrompt])

  const handleExport = useCallback(async (prompt: Prompt) => {
    await exportPrompt(prompt.id, 'json')
  }, [exportPrompt])

  const handleSortToggle = useCallback(() => {
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
  }, [])

  const handleRefresh = useCallback(() => {
    loadPrompts()
  }, [loadPrompts])

  const promptsToShow = filteredAndSortedPrompts
  const hasPrompts = promptsToShow.length > 0
  const hasError = prompts.error !== null

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Library className="h-5 w-5" />
              Prompt Library
              {prompts.data && (
                <Badge variant="secondary">
                  {prompts.data.total} prompts
                </Badge>
              )}
            </CardTitle>
            <div className="flex items-center gap-2">
              {/* View Mode Toggle */}
              <div className="flex items-center border rounded-md">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className="rounded-r-none"
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className="rounded-l-none"
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
              
              {onCreate && (
                <Button onClick={onCreate} className="flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  New Prompt
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search prompts by name, description, or variables..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
              {searchQuery && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
                >
                  ×
                </Button>
              )}
            </div>

            {/* Sort */}
            <div className="flex items-center gap-2">
              <Label className="text-sm whitespace-nowrap">Sort by:</Label>
              <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortOption)}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="name">Name</SelectItem>
                  <SelectItem value="updated">Updated</SelectItem>
                  <SelectItem value="created">Created</SelectItem>
                  <SelectItem value="variables">Variables</SelectItem>
                </SelectContent>
              </Select>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleSortToggle}
                className="px-2"
                title={`Sort ${sortDirection === 'asc' ? 'descending' : 'ascending'}`}
              >
                {sortDirection === 'asc' ? (
                  <SortAsc className="h-4 w-4" />
                ) : (
                  <SortDesc className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          {/* Results Summary */}
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              {isLoading ? 'Loading...' : `${promptsToShow.length} prompt${promptsToShow.length !== 1 ? 's' : ''}`}
              {searchQuery && ` matching "${searchQuery}"`}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              disabled={isLoading}
              className="text-xs"
            >
              {isLoading ? (
                <Loader2 className="h-3 w-3 animate-spin mr-1" />
              ) : (
                'Refresh'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Error State */}
      {hasError && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {prompts.error}
          </AlertDescription>
        </Alert>
      )}

      {/* Loading State */}
      {isLoading && !hasPrompts && (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>Loading prompts...</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {!isLoading && !hasPrompts && !hasError && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">
              {searchQuery ? 'No prompts found' : 'No prompts yet'}
            </h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery 
                ? `No prompts match "${searchQuery}". Try adjusting your search.`
                : 'Get started by creating your first prompt template.'
              }
            </p>
            {!searchQuery && onCreate && (
              <Button onClick={onCreate} className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Create First Prompt
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Prompts Grid/List */}
      {hasPrompts && (
        <div className={cn(
          viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
            : 'space-y-4'
        )}>
          {promptsToShow.map((prompt) => (
            <PromptCard
              key={prompt.id}
              prompt={prompt}
              onSelect={onSelect}
              onEdit={onEdit}
              onPreview={onPreview}
              onDuplicate={handleDuplicate}
              onDelete={handleDelete}
              onExport={handleExport}
              selected={selectedPrompt?.id === prompt.id}
              showActions={showActions}
              className={viewMode === 'list' ? 'w-full' : ''}
            />
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Prompt</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{promptToDelete?.name}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDelete}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default PromptLibrary
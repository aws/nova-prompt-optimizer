import React, { useState, useCallback, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'

import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Search, 
  Star, 
  Users, 
  Calendar,
  Code,
  Tag,
  Filter,
  Eye,
  Import
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useMetrics } from '@/hooks'
import type { MetricLibraryItem, CustomMetric } from '@/types/metric'
import { MetricCategory } from '@/types/metric'

interface MetricLibraryProps {
  onImport?: (metric: CustomMetric) => void
  onPreview?: (item: MetricLibraryItem) => void
  className?: string
}

const CATEGORY_LABELS: Record<string, string> = {
  [MetricCategory.ACCURACY]: 'Accuracy',
  [MetricCategory.CLASSIFICATION]: 'Classification',
  [MetricCategory.REGRESSION]: 'Regression',
  [MetricCategory.TEXT_SIMILARITY]: 'Text Similarity',
  [MetricCategory.NLP]: 'Natural Language Processing',
  [MetricCategory.SENTIMENT]: 'Sentiment Analysis',
  [MetricCategory.ENTITY_EXTRACTION]: 'Entity Extraction',
  [MetricCategory.CUSTOM]: 'Custom'
}

export function MetricLibrary({ 
  onImport, 
  onPreview,
  className 
}: MetricLibraryProps) {
  const {
    libraryItems,
    loading,
    error,
    loadLibrary,
    importMetric,
    clearError
  } = useMetrics()

  // Filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'name' | 'rating' | 'usage' | 'date'>('rating')
  const [showBuiltinOnly, setShowBuiltinOnly] = useState(false)

  // Load library on mount
  useEffect(() => {
    loadLibrary()
  }, [loadLibrary])

  // Filter and sort items
  const filteredItems = React.useMemo(() => {
    let items = libraryItems.filter(item => {
      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase()
        const matchesName = item.name.toLowerCase().includes(query)
        const matchesDescription = item.description.toLowerCase().includes(query)
        const matchesTags = item.tags.some(tag => tag.toLowerCase().includes(query))
        if (!matchesName && !matchesDescription && !matchesTags) {
          return false
        }
      }

      // Category filter
      if (selectedCategory !== 'all' && item.category !== selectedCategory) {
        return false
      }

      // Built-in filter
      if (showBuiltinOnly && !item.is_builtin) {
        return false
      }

      return true
    })

    // Sort items
    items.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name)
        case 'rating':
          return b.rating - a.rating
        case 'usage':
          return b.usage_count - a.usage_count
        case 'date':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        default:
          return 0
      }
    })

    return items
  }, [libraryItems, searchQuery, selectedCategory, sortBy, showBuiltinOnly])

  // Handle import
  const handleImport = useCallback(async (item: MetricLibraryItem) => {
    try {
      clearError()
      const importedMetric = await importMetric(item.id)
      onImport?.(importedMetric)
    } catch (error) {
      // Error is handled by the hook
    }
  }, [importMetric, onImport, clearError])

  // Handle search
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query)
    loadLibrary(selectedCategory !== 'all' ? selectedCategory : undefined, query.trim() || undefined)
  }, [selectedCategory, loadLibrary])

  // Handle category change
  const handleCategoryChange = useCallback((category: string) => {
    setSelectedCategory(category)
    loadLibrary(category !== 'all' ? category : undefined, searchQuery.trim() || undefined)
  }, [searchQuery, loadLibrary])

  // Format date
  const formatDate = useCallback((dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }, [])

  // Render star rating
  const renderRating = useCallback((rating: number) => {
    const stars = []
    const fullStars = Math.floor(rating)
    const hasHalfStar = rating % 1 >= 0.5

    for (let i = 0; i < fullStars; i++) {
      stars.push(<Star key={i} className="h-3 w-3 fill-yellow-400 text-yellow-400" />)
    }

    if (hasHalfStar) {
      stars.push(<Star key="half" className="h-3 w-3 fill-yellow-400/50 text-yellow-400" />)
    }

    const emptyStars = 5 - Math.ceil(rating)
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<Star key={`empty-${i}`} className="h-3 w-3 text-gray-300" />)
    }

    return <div className="flex items-center gap-0.5">{stars}</div>
  }, [])

  return (
    <div className={cn('space-y-4', className)}>
      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  placeholder="Search metrics..."
                  className="pl-10"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Category */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Category</label>
              <Select value={selectedCategory} onValueChange={handleCategoryChange} disabled={loading}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Sort */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Sort By</label>
              <Select value={sortBy} onValueChange={(value) => setSortBy(value as any)} disabled={loading}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="rating">Rating</SelectItem>
                  <SelectItem value="usage">Usage Count</SelectItem>
                  <SelectItem value="name">Name</SelectItem>
                  <SelectItem value="date">Date Added</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={showBuiltinOnly}
                onChange={(e) => setShowBuiltinOnly(e.target.checked)}
                disabled={loading}
                className="rounded"
              />
              Built-in metrics only
            </label>
            <div className="text-sm text-muted-foreground">
              {filteredItems.length} of {libraryItems.length} metrics
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <ScrollArea className="h-[500px]">
        <div className="space-y-4">
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
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
          ) : filteredItems.length > 0 ? (
            filteredItems.map((item) => (
              <Card key={item.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg flex items-center gap-2">
                        {item.name}
                        {item.is_builtin && (
                          <Badge variant="secondary" className="text-xs">
                            Built-in
                          </Badge>
                        )}
                      </CardTitle>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          {renderRating(item.rating)}
                          <span>({item.rating.toFixed(1)})</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {item.usage_count} uses
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(item.created_at)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {onPreview && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onPreview(item)}
                          disabled={loading}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleImport(item)}
                        disabled={loading}
                      >
                        <Import className="mr-2 h-4 w-4" />
                        Import
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <CardDescription className="mb-3">
                    {item.description}
                  </CardDescription>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex flex-wrap gap-1">
                      <Badge variant="outline" className="text-xs">
                        {CATEGORY_LABELS[item.category] || item.category}
                      </Badge>
                      {item.tags.slice(0, 3).map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          <Tag className="mr-1 h-2 w-2" />
                          {tag}
                        </Badge>
                      ))}
                      {item.tags.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{item.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                    
                    {item.author && (
                      <div className="text-xs text-muted-foreground">
                        by {item.author}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center text-muted-foreground">
                  <Code className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>No metrics found</p>
                  <p className="text-sm">Try adjusting your search criteria</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}

export default MetricLibrary
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { DatasetCard } from './DatasetCard';
import { LoadingSpinner } from '@/components/common/Loading';
import { cn } from '@/lib/utils';
import { 
  Search, 
  Filter, 
  SortAsc, 
  SortDesc, 
  Database, 
  AlertCircle,
  Trash2,
  RefreshCw
} from 'lucide-react';
import { Dataset } from '@/types/dataset';

interface DatasetListProps {
  datasets: Dataset[];
  selectedDataset?: Dataset;
  onSelect?: (dataset: Dataset) => void;
  onPreview?: (dataset: Dataset) => void;
  onEdit?: (dataset: Dataset) => void;
  onDelete?: (dataset: Dataset) => void;
  onDownload?: (dataset: Dataset) => void;
  onRefresh?: () => void;
  loading?: boolean;
  error?: string;
  className?: string;
  disabled?: boolean;
}

type SortField = 'name' | 'created_at' | 'file_size' | 'row_count';
type SortOrder = 'asc' | 'desc';
type FilterType = 'all' | 'csv' | 'json';

export const DatasetList: React.FC<DatasetListProps> = ({
  datasets,
  selectedDataset,
  onSelect,
  onPreview,
  onEdit,
  onDelete,
  onDownload,
  onRefresh,
  loading = false,
  error,
  className,
  disabled = false,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [datasetToDelete, setDatasetToDelete] = useState<Dataset | null>(null);

  // Filter and sort datasets
  const filteredAndSortedDatasets = React.useMemo(() => {
    let filtered = datasets;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(dataset => 
        dataset.name.toLowerCase().includes(query) ||
        dataset.description?.toLowerCase().includes(query) ||
        dataset.file_name.toLowerCase().includes(query) ||
        dataset.column_names.some(col => col.toLowerCase().includes(query))
      );
    }

    // Apply type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(dataset => dataset.file_type === filterType);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortField) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'created_at':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'file_size':
          aValue = a.file_size;
          bValue = b.file_size;
          break;
        case 'row_count':
          aValue = a.row_count;
          bValue = b.row_count;
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [datasets, searchQuery, sortField, sortOrder, filterType]);

  const handleDeleteClick = (dataset: Dataset) => {
    setDatasetToDelete(dataset);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (datasetToDelete && onDelete) {
      onDelete(datasetToDelete);
    }
    setDeleteDialogOpen(false);
    setDatasetToDelete(null);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setDatasetToDelete(null);
  };

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return null;
    return sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />;
  };

  const getFileTypeStats = () => {
    const stats = datasets.reduce((acc, dataset) => {
      acc[dataset.file_type] = (acc[dataset.file_type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    return stats;
  };

  const fileTypeStats = getFileTypeStats();

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
          <span className="ml-2">Loading datasets...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardContent className="py-6">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header with Stats */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Datasets
                <Badge variant="secondary">{datasets.length}</Badge>
              </CardTitle>
              <CardDescription>
                Manage your uploaded datasets for prompt optimization
              </CardDescription>
            </div>
            {onRefresh && (
              <Button variant="outline" size="sm" onClick={onRefresh} disabled={disabled}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {/* File Type Stats */}
          <div className="flex gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">File Types:</span>
              {Object.entries(fileTypeStats).map(([type, count]) => (
                <Badge key={type} variant="outline" className="text-xs">
                  {type.toUpperCase()}: {count}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search datasets by name, description, or columns..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Filter by Type */}
            <Select value={filterType} onValueChange={(value: FilterType) => setFilterType(value)}>
              <SelectTrigger className="w-[140px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="csv">CSV Only</SelectItem>
                <SelectItem value="json">JSON Only</SelectItem>
              </SelectContent>
            </Select>

            {/* Sort Options */}
            <div className="flex gap-2">
              <Button
                variant={sortField === 'name' ? 'default' : 'outline'}
                size="sm"
                onClick={() => toggleSort('name')}
              >
                Name {getSortIcon('name')}
              </Button>
              <Button
                variant={sortField === 'created_at' ? 'default' : 'outline'}
                size="sm"
                onClick={() => toggleSort('created_at')}
              >
                Date {getSortIcon('created_at')}
              </Button>
              <Button
                variant={sortField === 'row_count' ? 'default' : 'outline'}
                size="sm"
                onClick={() => toggleSort('row_count')}
              >
                Rows {getSortIcon('row_count')}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Dataset Grid */}
      {filteredAndSortedDatasets.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              {searchQuery || filterType !== 'all' ? 'No matching datasets' : 'No datasets found'}
            </h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery || filterType !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'Upload your first dataset to get started with prompt optimization'
              }
            </p>
            {(searchQuery || filterType !== 'all') && (
              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchQuery('');
                  setFilterType('all');
                }}
              >
                Clear Filters
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAndSortedDatasets.map((dataset) => (
            <DatasetCard
              key={dataset.id}
              dataset={dataset}
              selected={selectedDataset?.id === dataset.id}
              onSelect={onSelect}
              onPreview={onPreview}
              onEdit={onEdit}
              onDelete={handleDeleteClick}
              onDownload={onDownload}
              disabled={disabled}
            />
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Trash2 className="h-5 w-5 text-red-600" />
              Delete Dataset
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{datasetToDelete?.name}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                This will permanently delete the dataset and all associated data. Any optimization 
                experiments using this dataset may be affected.
              </AlertDescription>
            </Alert>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleDeleteCancel}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteConfirm}>
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Dataset
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import { 
  FileText, 
  Database, 
  Calendar, 
  MoreVertical, 
  Eye, 
  Edit, 
  Trash2, 
  Download,
  BarChart3,
  Layers
} from 'lucide-react';
import { Dataset } from '@/types/dataset';

interface DatasetCardProps {
  dataset: Dataset;
  selected?: boolean;
  onSelect?: (dataset: Dataset) => void;
  onPreview?: (dataset: Dataset) => void;
  onEdit?: (dataset: Dataset) => void;
  onDelete?: (dataset: Dataset) => void;
  onDownload?: (dataset: Dataset) => void;
  className?: string;
  disabled?: boolean;
}

export const DatasetCard: React.FC<DatasetCardProps> = ({
  dataset,
  selected = false,
  onSelect,
  onPreview,
  onEdit,
  onDelete,
  onDownload,
  className,
  disabled = false,
}) => {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getFileTypeIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'csv':
        return <FileText className="h-4 w-4 text-green-600" />;
      case 'json':
      case 'jsonl':
        return <Database className="h-4 w-4 text-blue-600" />;
      default:
        return <FileText className="h-4 w-4 text-gray-600" />;
    }
  };

  const handleCardClick = () => {
    if (!disabled && onSelect) {
      onSelect(dataset);
    }
  };

  return (
    <Card 
      className={cn(
        'cursor-pointer transition-all duration-200 hover:shadow-md',
        selected && 'ring-2 ring-primary ring-offset-2',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      onClick={handleCardClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1 flex-1 min-w-0">
            <CardTitle className="text-lg truncate">{dataset.name}</CardTitle>
            {dataset.description && (
              <CardDescription className="line-clamp-2">
                {dataset.description}
              </CardDescription>
            )}
          </div>
          <div className="flex items-center gap-2 ml-2">
            <Badge variant="outline" className="text-xs">
              {getFileTypeIcon(dataset.file_type)}
              <span className="ml-1">{dataset.file_type.toUpperCase()}</span>
            </Badge>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="h-8 w-8 p-0"
                  onClick={(e) => e.stopPropagation()}
                  disabled={disabled}
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {onPreview && (
                  <DropdownMenuItem onClick={(e) => {
                    e.stopPropagation();
                    onPreview(dataset);
                  }}>
                    <Eye className="mr-2 h-4 w-4" />
                    Preview Data
                  </DropdownMenuItem>
                )}
                {onEdit && (
                  <DropdownMenuItem onClick={(e) => {
                    e.stopPropagation();
                    onEdit(dataset);
                  }}>
                    <Edit className="mr-2 h-4 w-4" />
                    Edit Details
                  </DropdownMenuItem>
                )}
                {onDownload && (
                  <DropdownMenuItem onClick={(e) => {
                    e.stopPropagation();
                    onDownload(dataset);
                  }}>
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </DropdownMenuItem>
                )}
                {(onPreview || onEdit || onDownload) && onDelete && (
                  <DropdownMenuSeparator />
                )}
                {onDelete && (
                  <DropdownMenuItem 
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(dataset);
                    }}
                    className="text-red-600 focus:text-red-600"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Dataset Statistics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2 text-sm">
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Rows:</span>
            <span className="font-medium">{dataset.row_count.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Layers className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Columns:</span>
            <span className="font-medium">{dataset.column_names.length}</span>
          </div>
        </div>

        {/* File Information */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">File:</span>
            <span className="font-mono text-xs truncate max-w-[200px]" title={dataset.file_name}>
              {dataset.file_name}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Size:</span>
            <span>{formatFileSize(dataset.file_size)}</span>
          </div>
        </div>

        {/* Column Information */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Input Columns:</span>
            <Badge variant="default" className="text-xs">
              {dataset.input_columns.length}
            </Badge>
          </div>
          <div className="flex flex-wrap gap-1">
            {dataset.input_columns.slice(0, 3).map((column) => (
              <Badge key={column} variant="outline" className="text-xs">
                {column}
              </Badge>
            ))}
            {dataset.input_columns.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{dataset.input_columns.length - 3} more
              </Badge>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Output Columns:</span>
            <Badge variant="secondary" className="text-xs">
              {dataset.output_columns.length}
            </Badge>
          </div>
          <div className="flex flex-wrap gap-1">
            {dataset.output_columns.slice(0, 3).map((column) => (
              <Badge key={column} variant="secondary" className="text-xs">
                {column}
              </Badge>
            ))}
            {dataset.output_columns.length > 3 && (
              <Badge variant="secondary" className="text-xs">
                +{dataset.output_columns.length - 3} more
              </Badge>
            )}
          </div>
        </div>

        {/* Train/Test Split */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Train/Test Split:</span>
            <span className="text-xs">
              {Math.round(dataset.split_ratio * 100)}% / {Math.round((1 - dataset.split_ratio) * 100)}%
            </span>
          </div>
          <div className="flex gap-1 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-primary rounded-full"></div>
              <span>Train: {dataset.train_size.toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-secondary rounded-full"></div>
              <span>Test: {dataset.test_size.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </CardContent>

      <CardFooter className="pt-3 border-t">
        <div className="flex items-center gap-2 text-xs text-muted-foreground w-full">
          <Calendar className="h-3 w-3" />
          <span>Uploaded {formatDate(dataset.created_at)}</span>
        </div>
      </CardFooter>
    </Card>
  );
};
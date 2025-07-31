import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { DataTable } from '@/components/common/DataDisplay';
import { LoadingSpinner } from '@/components/common/Loading';
import { cn } from '@/lib/utils';
import { 
  Eye, 
  Table as TableIcon, 
  BarChart3, 
  AlertCircle, 
  ChevronLeft, 
  ChevronRight,
  Download,
  Layers,
  FileText
} from 'lucide-react';
import { Dataset, DatasetPreview as DatasetPreviewType } from '@/types/dataset';

interface DatasetPreviewProps {
  dataset: Dataset;
  preview?: DatasetPreviewType;
  onLoadPreview?: (datasetId: string, limit: number, offset: number) => void;
  onDownload?: (dataset: Dataset) => void;
  loading?: boolean;
  error?: string;
  className?: string;
}

const ROWS_PER_PAGE = 10;

export const DatasetPreview: React.FC<DatasetPreviewProps> = ({
  dataset,
  preview,
  onLoadPreview,
  onDownload,
  loading = false,
  error,
  className,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [activeTab, setActiveTab] = useState('preview');

  // Load preview data when component mounts or page changes
  useEffect(() => {
    if (onLoadPreview) {
      const offset = (currentPage - 1) * ROWS_PER_PAGE;
      onLoadPreview(dataset.id, ROWS_PER_PAGE, offset);
    }
  }, [dataset.id, currentPage, onLoadPreview]);

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
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getFileTypeIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'csv':
        return <FileText className="h-5 w-5 text-green-600" />;
      case 'json':
      case 'jsonl':
        return <FileText className="h-5 w-5 text-blue-600" />;
      default:
        return <FileText className="h-5 w-5 text-gray-600" />;
    }
  };

  const totalPages = preview ? Math.ceil(preview.total_rows / ROWS_PER_PAGE) : 1;

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  // Prepare table data
  const tableColumns = preview?.columns.map(column => ({
    key: column,
    header: column,
    render: (value: any) => {
      if (value === null || value === undefined) {
        return <span className="text-muted-foreground italic">null</span>;
      }
      if (typeof value === 'string' && value.length > 100) {
        return (
          <span title={value} className="truncate block max-w-[200px]">
            {value.substring(0, 100)}...
          </span>
        );
      }
      return <span>{String(value)}</span>;
    },
  })) || [];

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <CardTitle className="flex items-center gap-2">
                {getFileTypeIcon(dataset.file_type)}
                {dataset.name}
              </CardTitle>
              <CardDescription>
                {dataset.description || 'Dataset preview and statistics'}
              </CardDescription>
            </div>
            {onDownload && (
              <Button variant="outline" onClick={() => onDownload(dataset)}>
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-1">
              <div className="text-sm text-muted-foreground">Total Rows</div>
              <div className="text-2xl font-bold">{dataset.row_count.toLocaleString()}</div>
            </div>
            <div className="space-y-1">
              <div className="text-sm text-muted-foreground">Columns</div>
              <div className="text-2xl font-bold">{dataset.column_names.length}</div>
            </div>
            <div className="space-y-1">
              <div className="text-sm text-muted-foreground">File Size</div>
              <div className="text-2xl font-bold">{formatFileSize(dataset.file_size)}</div>
            </div>
            <div className="space-y-1">
              <div className="text-sm text-muted-foreground">File Type</div>
              <div className="text-2xl font-bold">{dataset.file_type.toUpperCase()}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="preview" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Data Preview
          </TabsTrigger>
          <TabsTrigger value="schema" className="flex items-center gap-2">
            <Layers className="h-4 w-4" />
            Schema
          </TabsTrigger>
          <TabsTrigger value="stats" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Statistics
          </TabsTrigger>
        </TabsList>

        {/* Data Preview Tab */}
        <TabsContent value="preview" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <TableIcon className="h-5 w-5" />
                  Data Preview
                </CardTitle>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  Showing rows {((currentPage - 1) * ROWS_PER_PAGE) + 1} - {Math.min(currentPage * ROWS_PER_PAGE, dataset.row_count)} of {dataset.row_count.toLocaleString()}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <LoadingSpinner size="lg" />
                  <span className="ml-2">Loading preview...</span>
                </div>
              ) : error ? (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              ) : preview && preview.rows.length > 0 ? (
                <div className="space-y-4">
                  <DataTable
                    data={preview.rows}
                    columns={tableColumns}
                    className="border rounded-md"
                  />
                  
                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-muted-foreground">
                        Page {currentPage} of {totalPages}
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handlePreviousPage}
                          disabled={currentPage === 1}
                        >
                          <ChevronLeft className="h-4 w-4" />
                          Previous
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleNextPage}
                          disabled={currentPage === totalPages}
                        >
                          Next
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <TableIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No data available</h3>
                  <p className="text-muted-foreground">Unable to load preview data for this dataset.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Schema Tab */}
        <TabsContent value="schema" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Dataset Schema</CardTitle>
              <CardDescription>
                Column definitions and data mapping configuration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* File Information */}
              <div className="space-y-4">
                <h4 className="font-semibold">File Information</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Filename:</span>
                    <div className="font-mono mt-1">{dataset.file_name}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Uploaded:</span>
                    <div className="mt-1">{formatDate(dataset.created_at)}</div>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Input Columns */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">Input Columns</h4>
                  <Badge variant="default">{dataset.input_columns.length} columns</Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {dataset.input_columns.map((column) => (
                    <Badge key={column} variant="outline" className="justify-start">
                      {column}
                    </Badge>
                  ))}
                </div>
              </div>

              <Separator />

              {/* Output Columns */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">Output Columns</h4>
                  <Badge variant="secondary">{dataset.output_columns.length} columns</Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {dataset.output_columns.map((column) => (
                    <Badge key={column} variant="secondary" className="justify-start">
                      {column}
                    </Badge>
                  ))}
                </div>
              </div>

              <Separator />

              {/* All Columns */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">All Columns</h4>
                  <Badge variant="outline">{dataset.column_names.length} total</Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {dataset.column_names.map((column) => {
                    const isInput = dataset.input_columns.includes(column);
                    const isOutput = dataset.output_columns.includes(column);
                    return (
                      <div key={column} className="flex items-center gap-2">
                        <Badge 
                          variant={isInput ? "default" : isOutput ? "secondary" : "outline"}
                          className="justify-start flex-1"
                        >
                          {column}
                        </Badge>
                        {isInput && <span className="text-xs text-muted-foreground">input</span>}
                        {isOutput && <span className="text-xs text-muted-foreground">output</span>}
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Statistics Tab */}
        <TabsContent value="stats" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Dataset Statistics</CardTitle>
              <CardDescription>
                Detailed information about your dataset structure and splits
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Basic Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center space-y-2">
                  <div className="text-3xl font-bold text-primary">{dataset.row_count.toLocaleString()}</div>
                  <div className="text-sm text-muted-foreground">Total Rows</div>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-3xl font-bold text-primary">{dataset.column_names.length}</div>
                  <div className="text-sm text-muted-foreground">Columns</div>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-3xl font-bold text-primary">{dataset.input_columns.length}</div>
                  <div className="text-sm text-muted-foreground">Input Features</div>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-3xl font-bold text-primary">{dataset.output_columns.length}</div>
                  <div className="text-sm text-muted-foreground">Output Labels</div>
                </div>
              </div>

              <Separator />

              {/* Train/Test Split */}
              <div className="space-y-4">
                <h4 className="font-semibold">Train/Test Split</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Split Ratio</span>
                    <Badge variant="outline">
                      {Math.round(dataset.split_ratio * 100)}% / {Math.round((1 - dataset.split_ratio) * 100)}%
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-primary rounded-full"></div>
                        Training Set
                      </span>
                      <span className="font-medium">{dataset.train_size.toLocaleString()} rows</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-secondary rounded-full"></div>
                        Test Set
                      </span>
                      <span className="font-medium">{dataset.test_size.toLocaleString()} rows</span>
                    </div>
                  </div>
                  
                  {/* Visual representation */}
                  <div className="w-full bg-secondary rounded-full h-2 overflow-hidden">
                    <div 
                      className="bg-primary h-full transition-all duration-300"
                      style={{ width: `${dataset.split_ratio * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              <Separator />

              {/* File Information */}
              <div className="space-y-4">
                <h4 className="font-semibold">File Information</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">File Name:</span>
                      <span className="font-mono">{dataset.file_name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">File Type:</span>
                      <Badge variant="outline">{dataset.file_type.toUpperCase()}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">File Size:</span>
                      <span>{formatFileSize(dataset.file_size)}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Created:</span>
                      <span>{formatDate(dataset.created_at)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Updated:</span>
                      <span>{formatDate(dataset.updated_at)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
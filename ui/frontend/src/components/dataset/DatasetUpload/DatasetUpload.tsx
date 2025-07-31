import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Form, FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage } from '@/components/ui/form';
import { FileDropzone } from './FileDropzone';
import { ColumnMapper } from './ColumnMapper';
import { cn } from '@/lib/utils';
import { Upload, FileText, Settings, CheckCircle, AlertCircle } from 'lucide-react';
import { Dataset, ColumnMapping } from '@/types/dataset';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const uploadFormSchema = z.object({
  name: z.string().min(1, 'Dataset name is required').max(100, 'Name must be less than 100 characters'),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
  split_ratio: z.number().min(0.1).max(0.9),
});

type UploadFormData = z.infer<typeof uploadFormSchema>;

interface DatasetUploadProps {
  onUploadComplete: (dataset: Dataset) => void;
  onUploadStart?: () => void;
  onUploadError?: (error: string) => void;
  className?: string;
  disabled?: boolean;
}

type UploadStep = 'file' | 'columns' | 'metadata' | 'uploading' | 'complete';

export const DatasetUpload: React.FC<DatasetUploadProps> = ({
  onUploadComplete,
  onUploadStart,
  onUploadError,
  className,
  disabled = false,
}) => {
  const [currentStep, setCurrentStep] = useState<UploadStep>('file');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [detectedColumns, setDetectedColumns] = useState<string[]>([]);
  const [columnMapping, setColumnMapping] = useState<ColumnMapping>({
    input_columns: [],
    output_columns: [],
  });
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const form = useForm<UploadFormData>({
    resolver: zodResolver(uploadFormSchema),
    defaultValues: {
      name: '',
      description: '',
      split_ratio: 0.8,
    },
  });

  // Detect columns when file is selected
  const detectColumns = useCallback(async (file: File) => {
    setIsProcessing(true);
    setUploadError(null);
    
    try {
      // For CSV files, read the first line to get headers
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        const text = await file.text();
        const firstLine = text.split('\n')[0];
        const columns = firstLine.split(',').map(col => col.trim().replace(/"/g, ''));
        setDetectedColumns(columns);
      }
      // For JSON files, try to detect keys from first object
      else if (file.type === 'application/json' || file.name.endsWith('.json') || file.name.endsWith('.jsonl')) {
        const text = await file.text();
        let firstObject: any = null;
        
        if (file.name.endsWith('.jsonl')) {
          // JSONL format - first line is first object
          const firstLine = text.split('\n')[0];
          if (firstLine.trim()) {
            firstObject = JSON.parse(firstLine);
          }
        } else {
          // Regular JSON - could be array or single object
          const parsed = JSON.parse(text);
          if (Array.isArray(parsed) && parsed.length > 0) {
            firstObject = parsed[0];
          } else if (typeof parsed === 'object') {
            firstObject = parsed;
          }
        }
        
        if (firstObject && typeof firstObject === 'object') {
          const columns = Object.keys(firstObject);
          setDetectedColumns(columns);
        } else {
          throw new Error('Could not detect columns from JSON structure');
        }
      }
      
      // Auto-generate dataset name from filename if not set
      if (!form.getValues('name')) {
        const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
        form.setValue('name', nameWithoutExt);
      }
      
      setCurrentStep('columns');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to analyze file structure';
      setUploadError(errorMessage);
      if (onUploadError) {
        onUploadError(errorMessage);
      }
    } finally {
      setIsProcessing(false);
    }
  }, [form, onUploadError]);

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    setUploadError(null);
    detectColumns(file);
  }, [detectColumns]);

  const handleFileRemove = useCallback(() => {
    setSelectedFile(null);
    setDetectedColumns([]);
    setColumnMapping({ input_columns: [], output_columns: [] });
    setCurrentStep('file');
    setUploadError(null);
  }, []);

  const handleColumnMappingChange = useCallback((mapping: ColumnMapping) => {
    setColumnMapping(mapping);
  }, []);

  const canProceedToMetadata = () => {
    return columnMapping.input_columns.length > 0 && columnMapping.output_columns.length > 0;
  };

  const handleProceedToMetadata = () => {
    if (canProceedToMetadata()) {
      setCurrentStep('metadata');
    }
  };

  const handleBackToColumns = () => {
    setCurrentStep('columns');
  };

  const handleBackToFile = () => {
    setCurrentStep('file');
  };

  const handleUpload = async (formData: UploadFormData) => {
    if (!selectedFile) return;
    
    setCurrentStep('uploading');
    setUploadProgress(0);
    setUploadError(null);
    
    if (onUploadStart) {
      onUploadStart();
    }

    try {
      // TODO: Replace with actual API call
      // const uploadRequest: DatasetUploadRequest = {
      //   file: selectedFile,
      //   input_columns: columnMapping.input_columns,
      //   output_columns: columnMapping.output_columns,
      //   split_ratio: formData.split_ratio,
      //   name: formData.name,
      //   description: formData.description,
      // };

      // Simulate upload progress (replace with actual API call)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.random() * 10;
        });
      }, 200);

      // TODO: Replace with actual API call
      // const dataset = await datasetApi.upload(uploadRequest, setUploadProgress);
      
      // Simulate API call for now
      await new Promise(resolve => setTimeout(resolve, 2000));
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Mock dataset response
      const mockDataset: Dataset = {
        id: `dataset-${Date.now()}`,
        name: formData.name,
        description: formData.description,
        file_name: selectedFile.name,
        file_type: selectedFile.name.endsWith('.csv') ? 'csv' : 'json',
        file_size: selectedFile.size,
        row_count: 1000, // Mock value
        column_names: detectedColumns,
        input_columns: columnMapping.input_columns,
        output_columns: columnMapping.output_columns,
        split_ratio: formData.split_ratio,
        train_size: Math.floor(1000 * formData.split_ratio),
        test_size: Math.floor(1000 * (1 - formData.split_ratio)),
        metadata: {},
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      setCurrentStep('complete');
      onUploadComplete(mockDataset);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      setUploadError(errorMessage);
      setCurrentStep('metadata');
      if (onUploadError) {
        onUploadError(errorMessage);
      }
    }
  };

  const resetUpload = () => {
    setCurrentStep('file');
    setSelectedFile(null);
    setDetectedColumns([]);
    setColumnMapping({ input_columns: [], output_columns: [] });
    setUploadProgress(0);
    setUploadError(null);
    form.reset();
  };

  const getStepIcon = (step: UploadStep) => {
    switch (step) {
      case 'file':
        return <FileText className="h-5 w-5" />;
      case 'columns':
        return <Settings className="h-5 w-5" />;
      case 'metadata':
        return <Upload className="h-5 w-5" />;
      case 'uploading':
        return <Upload className="h-5 w-5 animate-pulse" />;
      case 'complete':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
    }
  };

  const getStepTitle = (step: UploadStep) => {
    switch (step) {
      case 'file':
        return 'Select Dataset File';
      case 'columns':
        return 'Map Columns';
      case 'metadata':
        return 'Dataset Information';
      case 'uploading':
        return 'Processing Dataset';
      case 'complete':
        return 'Upload Complete';
    }
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Progress Steps */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            {(['file', 'columns', 'metadata', 'uploading'] as UploadStep[]).map((step, index) => (
              <div key={step} className="flex items-center">
                <div className={cn(
                  'flex items-center justify-center w-8 h-8 rounded-full border-2',
                  currentStep === step 
                    ? 'border-primary bg-primary text-primary-foreground'
                    : index < (['file', 'columns', 'metadata', 'uploading'] as UploadStep[]).indexOf(currentStep)
                    ? 'border-green-500 bg-green-500 text-white'
                    : 'border-muted-foreground bg-background'
                )}>
                  {getStepIcon(step)}
                </div>
                {index < 3 && (
                  <div className={cn(
                    'w-16 h-0.5 mx-2',
                    index < (['file', 'columns', 'metadata', 'uploading'] as UploadStep[]).indexOf(currentStep)
                      ? 'bg-green-500'
                      : 'bg-muted-foreground/30'
                  )} />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Step Content */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {getStepIcon(currentStep)}
            {getStepTitle(currentStep)}
          </CardTitle>
          <CardDescription>
            {currentStep === 'file' && 'Upload a CSV or JSON file containing your dataset'}
            {currentStep === 'columns' && 'Specify which columns contain input and output data'}
            {currentStep === 'metadata' && 'Provide additional information about your dataset'}
            {currentStep === 'uploading' && 'Processing your dataset and creating train/test splits'}
            {currentStep === 'complete' && 'Your dataset has been successfully uploaded and processed'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* File Selection Step */}
          {currentStep === 'file' && (
            <FileDropzone
              onFileSelect={handleFileSelect}
              onFileRemove={handleFileRemove}
              disabled={disabled || isProcessing}
              uploadProgress={isProcessing ? 50 : undefined}
              error={uploadError || undefined}
            />
          )}

          {/* Column Mapping Step */}
          {currentStep === 'columns' && (
            <div className="space-y-4">
              <ColumnMapper
                availableColumns={detectedColumns}
                onMappingChange={handleColumnMappingChange}
                disabled={disabled}
              />
              <div className="flex justify-between">
                <Button variant="outline" onClick={handleBackToFile}>
                  Back to File Selection
                </Button>
                <Button 
                  onClick={handleProceedToMetadata}
                  disabled={!canProceedToMetadata()}
                >
                  Continue to Dataset Info
                </Button>
              </div>
            </div>
          )}

          {/* Metadata Step */}
          {currentStep === 'metadata' && (
            <Form {...form}>
              <form onSubmit={form.handleSubmit(handleUpload)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Dataset Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter a name for your dataset" {...field} />
                      </FormControl>
                      <FormDescription>
                        A descriptive name to identify your dataset
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Description (Optional)</FormLabel>
                      <FormControl>
                        <Textarea 
                          placeholder="Describe what this dataset contains and its intended use"
                          className="min-h-[80px]"
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>
                        Additional details about your dataset
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="split_ratio"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Train/Test Split Ratio</FormLabel>
                      <FormControl>
                        <div className="space-y-2">
                          <Input
                            type="number"
                            min="0.1"
                            max="0.9"
                            step="0.1"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                          <div className="text-sm text-muted-foreground">
                            Training: {Math.round(field.value * 100)}% • Testing: {Math.round((1 - field.value) * 100)}%
                          </div>
                        </div>
                      </FormControl>
                      <FormDescription>
                        Proportion of data to use for training (0.1 to 0.9)
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {uploadError && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{uploadError}</AlertDescription>
                  </Alert>
                )}

                <div className="flex justify-between">
                  <Button type="button" variant="outline" onClick={handleBackToColumns}>
                    Back to Column Mapping
                  </Button>
                  <Button type="submit" disabled={disabled}>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Dataset
                  </Button>
                </div>
              </form>
            </Form>
          )}

          {/* Uploading Step */}
          {currentStep === 'uploading' && (
            <div className="space-y-4 text-center">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Processing dataset...</span>
                  <span>{Math.round(uploadProgress)}%</span>
                </div>
                <Progress value={uploadProgress} className="w-full" />
              </div>
              <p className="text-sm text-muted-foreground">
                This may take a few moments depending on your dataset size
              </p>
            </div>
          )}

          {/* Complete Step */}
          {currentStep === 'complete' && (
            <div className="text-center space-y-4">
              <CheckCircle className="h-16 w-16 text-green-600 mx-auto" />
              <div className="space-y-2">
                <h3 className="text-lg font-semibold">Dataset uploaded successfully!</h3>
                <p className="text-muted-foreground">
                  Your dataset has been processed and is ready for prompt optimization.
                </p>
              </div>
              <Button onClick={resetUpload} variant="outline">
                Upload Another Dataset
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
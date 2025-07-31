import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import { Upload, File, X, AlertCircle, CheckCircle } from 'lucide-react';

interface FileDropzoneProps {
  onFileSelect: (file: File) => void;
  onFileRemove?: () => void;
  acceptedFileTypes?: string[];
  maxFileSize?: number; // in bytes
  disabled?: boolean;
  className?: string;
  uploadProgress?: number;
  error?: string | null;
  success?: boolean;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFileSelect,
  onFileRemove,
  maxFileSize = 50 * 1024 * 1024, // 50MB for datasets
  disabled = false,
  className,
  uploadProgress,
  error,
  success = false,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json', '.jsonl'],
    },
    maxSize: maxFileSize,
    multiple: false,
    disabled,
  });

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (onFileRemove) {
      onFileRemove();
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={cn('space-y-4', className)}>
      <Card>
        <CardContent className="p-6">
          <div
            {...getRootProps()}
            className={cn(
              'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
              isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25',
              disabled && 'cursor-not-allowed opacity-50',
              success && 'border-green-500 bg-green-50 dark:bg-green-950',
              error && 'border-red-500 bg-red-50 dark:bg-red-950'
            )}
          >
            <input {...getInputProps()} />
            
            <div className="flex flex-col items-center space-y-4">
              {success ? (
                <CheckCircle className="h-12 w-12 text-green-600" />
              ) : error ? (
                <AlertCircle className="h-12 w-12 text-red-600" />
              ) : (
                <Upload className="h-12 w-12 text-muted-foreground" />
              )}
              
              <div className="space-y-2">
                <p className="text-lg font-medium">
                  {isDragActive
                    ? 'Drop the dataset file here'
                    : success
                    ? 'Dataset file ready for processing!'
                    : 'Drag & drop your dataset file here, or click to browse'}
                </p>
                <p className="text-sm text-muted-foreground">
                  Supported formats: CSV, JSON, JSONL
                </p>
                <p className="text-xs text-muted-foreground">
                  Maximum file size: {formatFileSize(maxFileSize)}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Selected File Display */}
      {selectedFile && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <File className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(selectedFile.size)} • {selectedFile.type || 'Unknown type'}
                  </p>
                </div>
              </div>
              {!disabled && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleRemoveFile}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
            
            {uploadProgress !== undefined && uploadProgress < 100 && (
              <div className="mt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Processing dataset...</span>
                  <span>{Math.round(uploadProgress)}%</span>
                </div>
                <Progress value={uploadProgress} className="w-full" />
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* File Rejection Errors */}
      {fileRejections.length > 0 && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {fileRejections.map(({ file, errors }) => (
              <div key={file.name} className="space-y-1">
                <strong>{file.name}:</strong>
                <ul className="list-disc list-inside ml-4">
                  {errors.map((error, index) => (
                    <li key={index} className="text-sm">
                      {error.code === 'file-too-large' 
                        ? `File is too large. Maximum size is ${formatFileSize(maxFileSize)}`
                        : error.code === 'file-invalid-type'
                        ? 'Invalid file type. Please upload a CSV, JSON, or JSONL file'
                        : error.message
                      }
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </AlertDescription>
        </Alert>
      )}

      {/* Custom Error */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
};
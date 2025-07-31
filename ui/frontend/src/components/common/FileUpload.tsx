import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';

import { cn } from '@/lib/utils';
import { Upload, File, X, AlertCircle, CheckCircle } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove?: () => void;
  acceptedFileTypes?: string[];
  maxFileSize?: number; // in bytes
  multiple?: boolean;
  disabled?: boolean;
  className?: string;
  uploadProgress?: number;
  error?: string;
  success?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onFileRemove,
  acceptedFileTypes = ['.csv', '.json', '.jsonl'],
  maxFileSize = 10 * 1024 * 1024, // 10MB
  multiple = false,
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
    accept: acceptedFileTypes.reduce((acc, type) => {
      acc[type] = [];
      return acc;
    }, {} as Record<string, string[]>),
    maxSize: maxFileSize,
    multiple,
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
              success && 'border-green-500 bg-green-50',
              error && 'border-red-500 bg-red-50'
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
                    ? 'Drop the file here'
                    : success
                    ? 'File uploaded successfully!'
                    : 'Drag & drop a file here, or click to browse'}
                </p>
                <p className="text-sm text-muted-foreground">
                  Supported formats: {acceptedFileTypes.join(', ')}
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
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRemoveFile}
                disabled={disabled}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            {uploadProgress !== undefined && uploadProgress < 100 && (
              <div className="mt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Uploading...</span>
                  <span>{uploadProgress}%</span>
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
              <div key={file.name}>
                <strong>{file.name}:</strong>{' '}
                {errors.map((error) => error.message).join(', ')}
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
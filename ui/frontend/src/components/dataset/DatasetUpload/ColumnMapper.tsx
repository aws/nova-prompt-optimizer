import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';
import { Plus, X, AlertCircle, Info } from 'lucide-react';
import { ColumnMapping } from '@/types/dataset';

interface ColumnMapperProps {
  availableColumns: string[];
  onMappingChange: (mapping: ColumnMapping) => void;
  initialMapping?: ColumnMapping;
  className?: string;
  disabled?: boolean;
}

export const ColumnMapper: React.FC<ColumnMapperProps> = ({
  availableColumns,
  onMappingChange,
  initialMapping,
  className,
  disabled = false,
}) => {
  const [inputColumns, setInputColumns] = useState<string[]>(
    initialMapping?.input_columns || []
  );
  const [outputColumns, setOutputColumns] = useState<string[]>(
    initialMapping?.output_columns || []
  );
  const [newInputColumn, setNewInputColumn] = useState('');
  const [newOutputColumn, setNewOutputColumn] = useState('');
  const [errors, setErrors] = useState<string[]>([]);

  // Update parent when mapping changes
  useEffect(() => {
    const mapping: ColumnMapping = {
      input_columns: inputColumns,
      output_columns: outputColumns,
    };
    onMappingChange(mapping);
  }, [inputColumns, outputColumns, onMappingChange]);

  // Validate mapping
  useEffect(() => {
    const newErrors: string[] = [];
    
    if (inputColumns.length === 0) {
      newErrors.push('At least one input column is required');
    }
    
    if (outputColumns.length === 0) {
      newErrors.push('At least one output column is required');
    }
    
    // Check for invalid column names
    const invalidInputs = inputColumns.filter(col => !availableColumns.includes(col));
    const invalidOutputs = outputColumns.filter(col => !availableColumns.includes(col));
    
    if (invalidInputs.length > 0) {
      newErrors.push(`Invalid input columns: ${invalidInputs.join(', ')}`);
    }
    
    if (invalidOutputs.length > 0) {
      newErrors.push(`Invalid output columns: ${invalidOutputs.join(', ')}`);
    }
    
    // Check for overlapping columns
    const overlap = inputColumns.filter(col => outputColumns.includes(col));
    if (overlap.length > 0) {
      newErrors.push(`Columns cannot be both input and output: ${overlap.join(', ')}`);
    }
    
    setErrors(newErrors);
  }, [inputColumns, outputColumns, availableColumns]);

  const addInputColumn = () => {
    if (newInputColumn.trim() && availableColumns.includes(newInputColumn.trim())) {
      if (!inputColumns.includes(newInputColumn.trim())) {
        setInputColumns([...inputColumns, newInputColumn.trim()]);
      }
      setNewInputColumn('');
    }
  };

  const addOutputColumn = () => {
    if (newOutputColumn.trim() && availableColumns.includes(newOutputColumn.trim())) {
      if (!outputColumns.includes(newOutputColumn.trim())) {
        setOutputColumns([...outputColumns, newOutputColumn.trim()]);
      }
      setNewOutputColumn('');
    }
  };

  const removeInputColumn = (column: string) => {
    setInputColumns(inputColumns.filter(col => col !== column));
  };

  const removeOutputColumn = (column: string) => {
    setOutputColumns(outputColumns.filter(col => col !== column));
  };

  const handleInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addInputColumn();
    }
  };

  const handleOutputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addOutputColumn();
    }
  };

  const getAvailableInputColumns = () => {
    return availableColumns.filter(col => !inputColumns.includes(col) && !outputColumns.includes(col));
  };

  const getAvailableOutputColumns = () => {
    return availableColumns.filter(col => !outputColumns.includes(col) && !inputColumns.includes(col));
  };

  return (
    <div className={cn('space-y-6', className)}>
      <Card>
        <CardHeader>
          <CardTitle>Column Mapping</CardTitle>
          <CardDescription>
            Specify which columns contain input data (features) and which contain output data (labels/targets)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Available Columns */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Available Columns</Label>
            <div className="flex flex-wrap gap-2 p-3 bg-muted/50 rounded-md min-h-[2.5rem]">
              {availableColumns.length > 0 ? (
                availableColumns.map((column) => (
                  <Badge key={column} variant="outline" className="text-xs">
                    {column}
                  </Badge>
                ))
              ) : (
                <span className="text-sm text-muted-foreground">No columns detected</span>
              )}
            </div>
          </div>

          <Separator />

          {/* Input Columns */}
          <div className="space-y-3">
            <div>
              <Label className="text-sm font-medium">Input Columns</Label>
              <p className="text-xs text-muted-foreground mt-1">
                Columns that contain the input data or features for your model
              </p>
            </div>
            
            <div className="flex flex-wrap gap-2 p-3 border rounded-md min-h-[2.5rem]">
              {inputColumns.map((column) => (
                <Badge key={column} variant="default" className="text-xs">
                  {column}
                  {!disabled && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="ml-1 h-auto p-0 hover:bg-transparent"
                      onClick={() => removeInputColumn(column)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  )}
                </Badge>
              ))}
              {inputColumns.length === 0 && (
                <span className="text-sm text-muted-foreground">No input columns selected</span>
              )}
            </div>

            {!disabled && (
              <div className="flex gap-2">
                <Input
                  placeholder="Type column name or select from available columns"
                  value={newInputColumn}
                  onChange={(e) => setNewInputColumn(e.target.value)}
                  onKeyPress={handleInputKeyPress}
                  list="input-columns-list"
                />
                <datalist id="input-columns-list">
                  {getAvailableInputColumns().map((column) => (
                    <option key={column} value={column} />
                  ))}
                </datalist>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={addInputColumn}
                  disabled={!newInputColumn.trim() || !availableColumns.includes(newInputColumn.trim())}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>

          <Separator />

          {/* Output Columns */}
          <div className="space-y-3">
            <div>
              <Label className="text-sm font-medium">Output Columns</Label>
              <p className="text-xs text-muted-foreground mt-1">
                Columns that contain the expected output, labels, or target values
              </p>
            </div>
            
            <div className="flex flex-wrap gap-2 p-3 border rounded-md min-h-[2.5rem]">
              {outputColumns.map((column) => (
                <Badge key={column} variant="secondary" className="text-xs">
                  {column}
                  {!disabled && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="ml-1 h-auto p-0 hover:bg-transparent"
                      onClick={() => removeOutputColumn(column)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  )}
                </Badge>
              ))}
              {outputColumns.length === 0 && (
                <span className="text-sm text-muted-foreground">No output columns selected</span>
              )}
            </div>

            {!disabled && (
              <div className="flex gap-2">
                <Input
                  placeholder="Type column name or select from available columns"
                  value={newOutputColumn}
                  onChange={(e) => setNewOutputColumn(e.target.value)}
                  onKeyPress={handleOutputKeyPress}
                  list="output-columns-list"
                />
                <datalist id="output-columns-list">
                  {getAvailableOutputColumns().map((column) => (
                    <option key={column} value={column} />
                  ))}
                </datalist>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={addOutputColumn}
                  disabled={!newOutputColumn.trim() || !availableColumns.includes(newOutputColumn.trim())}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>

          {/* Validation Errors */}
          {errors.length > 0 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                <ul className="list-disc list-inside space-y-1">
                  {errors.map((error, index) => (
                    <li key={index} className="text-sm">{error}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}

          {/* Help Text */}
          {errors.length === 0 && (inputColumns.length > 0 || outputColumns.length > 0) && (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>Mapping Summary:</strong> {inputColumns.length} input column(s) and {outputColumns.length} output column(s) selected.
                {inputColumns.length > 0 && outputColumns.length > 0 && 
                  " Your dataset is ready for processing!"
                }
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
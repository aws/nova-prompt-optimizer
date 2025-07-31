import { BaseEntity } from './common'

export interface Dataset extends BaseEntity {
  name: string
  description?: string
  file_name: string
  file_type: 'csv' | 'json'
  file_size: number
  row_count: number
  column_names: string[]
  input_columns: string[]
  output_columns: string[]
  split_ratio: number
  train_size: number
  test_size: number
  metadata: Record<string, any>
}

export interface DatasetPreview {
  columns: string[]
  rows: Record<string, any>[]
  total_rows: number
}

export interface DatasetUploadRequest {
  file: File
  input_columns: string[]
  output_columns: string[]
  split_ratio?: number
  name?: string
  description?: string
}

export interface ColumnMapping {
  input_columns: string[]
  output_columns: string[]
}

export interface DatasetStats {
  total_datasets: number
  total_rows: number
  file_types: Record<string, number>
  recent_uploads: Dataset[]
}
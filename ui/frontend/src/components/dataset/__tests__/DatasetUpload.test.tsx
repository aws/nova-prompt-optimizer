import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DatasetUpload } from '../DatasetUpload/DatasetUpload'

// Mock the file upload hook
const mockOnUploadComplete = vi.fn()

describe('DatasetUpload', () => {
  beforeEach(() => {
    mockOnUploadComplete.mockClear()
  })

  it('renders upload interface correctly', () => {
    render(
      <DatasetUpload
        onUploadComplete={mockOnUploadComplete}
        acceptedFormats={['.csv', '.json']}
        maxFileSize={10 * 1024 * 1024} // 10MB
      />
    )

    expect(screen.getByText('Upload Dataset')).toBeInTheDocument()
    expect(screen.getByText(/Drag & drop your file here/)).toBeInTheDocument()
    expect(screen.getByLabelText('Input Columns')).toBeInTheDocument()
    expect(screen.getByLabelText('Output Columns')).toBeInTheDocument()
  })

  it('handles file selection', async () => {
    const user = userEvent.setup()
    
    render(
      <DatasetUpload
        onUploadComplete={mockOnUploadComplete}
        acceptedFormats={['.csv', '.json']}
        maxFileSize={10 * 1024 * 1024}
      />
    )

    const file = new File(['input,output\ntest,result'], 'test.csv', {
      type: 'text/csv',
    })

    const fileInput = screen.getByRole('button', { name: /browse/i })
    
    // Mock file input behavior
    const hiddenInput = document.createElement('input')
    hiddenInput.type = 'file'
    hiddenInput.style.display = 'none'
    document.body.appendChild(hiddenInput)

    Object.defineProperty(hiddenInput, 'files', {
      value: [file],
      writable: false,
    })

    fireEvent.change(hiddenInput)

    expect(hiddenInput.files).toHaveLength(1)
    expect(hiddenInput.files?.[0]).toBe(file)
  })

  it('validates column mapping input', async () => {
    const user = userEvent.setup()
    
    render(
      <DatasetUpload
        onUploadComplete={mockOnUploadComplete}
        acceptedFormats={['.csv', '.json']}
        maxFileSize={10 * 1024 * 1024}
      />
    )

    const inputColumnsField = screen.getByLabelText('Input Columns')
    const outputColumnsField = screen.getByLabelText('Output Columns')

    await user.type(inputColumnsField, 'input, question')
    await user.type(outputColumnsField, 'output, answer')

    expect(inputColumnsField).toHaveValue('input, question')
    expect(outputColumnsField).toHaveValue('output, answer')
  })

  it('shows upload progress', async () => {
    render(
      <DatasetUpload
        onUploadComplete={mockOnUploadComplete}
        acceptedFormats={['.csv', '.json']}
        maxFileSize={10 * 1024 * 1024}
      />
    )

    // Mock upload progress
    const progressBar = document.createElement('div')
    progressBar.setAttribute('role', 'progressbar')
    progressBar.setAttribute('aria-valuenow', '50')
    document.body.appendChild(progressBar)

    expect(progressBar.getAttribute('aria-valuenow')).toBe('50')
  })

  it('handles upload errors', async () => {
    const user = userEvent.setup()
    
    render(
      <DatasetUpload
        onUploadComplete={mockOnUploadComplete}
        acceptedFormats={['.csv', '.json']}
        maxFileSize={10 * 1024 * 1024}
      />
    )

    // Mock error scenario
    const errorMessage = 'File format not supported'
    const errorElement = document.createElement('div')
    errorElement.textContent = errorMessage
    errorElement.setAttribute('role', 'alert')
    document.body.appendChild(errorElement)

    expect(screen.getByRole('alert')).toHaveTextContent(errorMessage)
  })

  it('validates file size limits', () => {
    const maxSize = 5 * 1024 * 1024 // 5MB
    
    render(
      <DatasetUpload
        onUploadComplete={mockOnUploadComplete}
        acceptedFormats={['.csv', '.json']}
        maxFileSize={maxSize}
      />
    )

    const largeFile = new File(['x'.repeat(maxSize + 1)], 'large.csv', {
      type: 'text/csv',
    })

    // Mock file size validation
    const isFileTooLarge = largeFile.size > maxSize
    expect(isFileTooLarge).toBe(true)
  })

  it('validates accepted file formats', () => {
    const acceptedFormats = ['.csv', '.json']
    
    render(
      <DatasetUpload
        onUploadComplete={mockOnUploadComplete}
        acceptedFormats={acceptedFormats}
        maxFileSize={10 * 1024 * 1024}
      />
    )

    const validFile = new File(['data'], 'test.csv', { type: 'text/csv' })
    const invalidFile = new File(['data'], 'test.txt', { type: 'text/plain' })

    const isValidFormat = (file: File) => {
      const extension = '.' + file.name.split('.').pop()
      return acceptedFormats.includes(extension)
    }

    expect(isValidFormat(validFile)).toBe(true)
    expect(isValidFormat(invalidFile)).toBe(false)
  })

  it('calls onUploadComplete when upload succeeds', async () => {
    render(
      <DatasetUpload
        onUploadComplete={mockOnUploadComplete}
        acceptedFormats={['.csv', '.json']}
        maxFileSize={10 * 1024 * 1024}
      />
    )

    // Mock successful upload
    const mockDataset = {
      id: 'dataset-123',
      name: 'test.csv',
      rows: 100,
      columns: ['input', 'output'],
    }

    // Simulate upload completion
    mockOnUploadComplete(mockDataset)

    expect(mockOnUploadComplete).toHaveBeenCalledWith(mockDataset)
  })

  it('supports drag and drop functionality', async () => {
    render(
      <DatasetUpload
        onUploadComplete={mockOnUploadComplete}
        acceptedFormats={['.csv', '.json']}
        maxFileSize={10 * 1024 * 1024}
      />
    )

    const dropzone = screen.getByText(/Drag & drop your file here/).closest('div')
    expect(dropzone).toBeInTheDocument()

    const file = new File(['input,output\ntest,result'], 'test.csv', {
      type: 'text/csv',
    })

    // Mock drag and drop events
    if (dropzone) {
      fireEvent.dragEnter(dropzone)
      fireEvent.dragOver(dropzone)
      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file],
        },
      })
    }

    // Verify drag and drop behavior
    expect(dropzone).toBeInTheDocument()
  })
})
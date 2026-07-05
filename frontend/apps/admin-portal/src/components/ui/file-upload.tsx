'use client'

import { useState, useRef, ChangeEvent } from 'react'
import { Upload, X, File, FileText, Image as ImageIcon } from 'lucide-react'
import { Button } from './button'
import { cn } from '@/lib/utils'

interface FileUploadProps {
  onFileSelect: (files: File[]) => void
  multiple?: boolean
  accept?: string
  maxSize?: number // in MB
  maxFiles?: number
  className?: string
  disabled?: boolean
}

export function FileUpload({
  onFileSelect,
  multiple = false,
  accept,
  maxSize = 10,
  maxFiles = 5,
  className,
  disabled = false,
}: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > maxSize * 1024 * 1024) {
      return `File size must be less than ${maxSize}MB`
    }

    // Check file type if accept is specified
    if (accept) {
      const acceptedTypes = accept.split(',').map(t => t.trim())
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
      const isAccepted = acceptedTypes.some(type => {
        if (type.startsWith('.')) {
          return fileExtension === type.toLowerCase()
        }
        if (type.endsWith('/*')) {
          return file.type.startsWith(type.replace('/*', ''))
        }
        return file.type === type
      })

      if (!isAccepted) {
        return `File type not accepted. Allowed: ${accept}`
      }
    }

    return null
  }

  const handleFiles = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const newFiles = Array.from(selectedFiles)
    const validFiles: File[] = []
    let errorMessage = ''

    for (const file of newFiles) {
      const error = validateFile(file)
      if (error) {
        errorMessage = error
        break
      }
      validFiles.push(file)
    }

    if (errorMessage) {
      setError(errorMessage)
      return
    }

    const totalFiles = multiple ? [...files, ...validFiles] : validFiles
    
    if (totalFiles.length > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`)
      return
    }

    setError('')
    setFiles(totalFiles)
    onFileSelect(totalFiles)
  }

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!disabled) {
      setIsDragging(true)
    }
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    if (disabled) return

    handleFiles(e.dataTransfer.files)
  }

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
  }

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    setFiles(newFiles)
    onFileSelect(newFiles)
    setError('')
  }

  const openFileBrowser = () => {
    fileInputRef.current?.click()
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return ImageIcon
    if (file.type.includes('pdf')) return FileText
    return File
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className={cn('w-full', className)}>
      {/* Drop Zone */}
      <div
        className={cn(
          'relative border-2 border-dashed rounded-lg p-8 transition-colors',
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400',
          disabled && 'opacity-50 cursor-not-allowed',
          'cursor-pointer'
        )}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={openFileBrowser}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          multiple={multiple}
          accept={accept}
          onChange={handleFileInput}
          disabled={disabled}
        />

        <div className="flex flex-col items-center justify-center text-center">
          <Upload className="h-12 w-12 text-gray-400 mb-4" />
          <p className="text-sm font-medium text-gray-700 mb-1">
            {isDragging ? 'Drop files here' : 'Click to upload or drag and drop'}
          </p>
          <p className="text-xs text-gray-500">
            {accept ? `Accepted: ${accept}` : 'All file types accepted'}
            {' • '}
            Max {maxSize}MB per file
            {multiple && ` • Up to ${maxFiles} files`}
          </p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
          {error}
        </div>
      )}

      {/* Selected Files */}
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-sm font-medium text-gray-700">
            Selected Files ({files.length})
          </p>
          {files.map((file, index) => {
            const FileIcon = getFileIcon(file)
            return (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <FileIcon className="h-5 w-5 text-gray-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 flex-shrink-0"
                  onClick={(e) => {
                    e.stopPropagation()
                    removeFile(index)
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

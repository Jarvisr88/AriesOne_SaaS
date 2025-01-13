/**
 * Image uploader component with preview and progress tracking.
 */
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { ImageProcessingOptions, ImageUploadResult } from '../types';
import { Progress } from './Progress';
import { ImagePreview } from './ImagePreview';

interface ImageUploaderProps {
  onUpload?: (result: ImageUploadResult) => void;
  onError?: (error: Error) => void;
  options?: ImageProcessingOptions;
  maxSize?: number;
  accept?: string[];
  multiple?: boolean;
  companyId: string;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  onUpload,
  onError,
  options = {},
  maxSize = 10 * 1024 * 1024, // 10MB
  accept = ['image/jpeg', 'image/png', 'image/tiff'],
  multiple = false,
  companyId,
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [progress, setProgress] = useState<number>(0);
  const [uploading, setUploading] = useState<boolean>(false);
  const [preview, setPreview] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
    if (acceptedFiles.length > 0) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: accept.join(','),
    maxSize,
    multiple,
  });

  const uploadFiles = async () => {
    setUploading(true);
    setProgress(0);

    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('companyId', companyId);
        formData.append('options', JSON.stringify(options));

        const response = await fetch('/api/imaging/upload', {
          method: 'POST',
          body: formData,
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          },
        });

        if (!response.ok) {
          throw new Error('Upload failed');
        }

        const result: ImageUploadResult = await response.json();
        
        if (onUpload) {
          onUpload(result);
        }
      }
    } catch (error) {
      if (onError) {
        onError(error as Error);
      }
    } finally {
      setUploading(false);
      setProgress(0);
      setFiles([]);
      setPreview(null);
    }
  };

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`p-8 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-500'
        }`}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p className="text-blue-500">Drop the files here...</p>
        ) : (
          <div className="space-y-2">
            <p className="text-gray-600">
              Drag and drop files here, or click to select files
            </p>
            <p className="text-sm text-gray-500">
              {accept.join(', ')} files up to {maxSize / (1024 * 1024)}MB
            </p>
          </div>
        )}
      </div>

      {preview && (
        <div className="mt-4">
          <ImagePreview src={preview} alt="Upload preview" />
        </div>
      )}

      {files.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              {files.length} file(s) selected
            </div>
            <button
              onClick={uploadFiles}
              disabled={uploading}
              className={`px-4 py-2 rounded-md text-white ${
                uploading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>

          {uploading && <Progress value={progress} />}

          <ul className="divide-y divide-gray-200">
            {files.map((file) => (
              <li key={file.name} className="py-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {file.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setFiles(files.filter((f) => f !== file));
                      if (files.length === 1) {
                        setPreview(null);
                      }
                    }}
                    className="text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

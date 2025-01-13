/**
 * Image viewer component with zoom and pan capabilities.
 */
import React, { useState, useRef, useEffect } from 'react';
import { ImageMetadata } from '../types';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';

interface ImageViewerProps {
  image: ImageMetadata;
  onClose?: () => void;
  onDownload?: () => void;
  showMetadata?: boolean;
}

export const ImageViewer: React.FC<ImageViewerProps> = ({
  image,
  onClose,
  onDownload,
  showMetadata = true,
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const img = new Image();
    img.src = image.url;
    img.onload = () => setLoading(false);
    img.onerror = () => setError('Failed to load image');
  }, [image.url]);

  const handleDownload = async () => {
    if (onDownload) {
      onDownload();
      return;
    }

    try {
      const response = await fetch(image.url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = image.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download image:', error);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black bg-opacity-75 flex items-center justify-center">
      <div className="relative w-full h-full max-w-7xl mx-auto p-4">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white hover:text-gray-300 z-10"
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Image container */}
        <div className="h-full flex flex-col">
          <div className="flex-1 relative">
            {loading ? (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
              </div>
            ) : error ? (
              <div className="absolute inset-0 flex items-center justify-center text-white">
                {error}
              </div>
            ) : (
              <TransformWrapper>
                <TransformComponent>
                  <img
                    ref={imageRef}
                    src={image.url}
                    alt={image.filename}
                    className="max-h-full w-auto mx-auto"
                  />
                </TransformComponent>
              </TransformWrapper>
            )}
          </div>

          {/* Controls and metadata */}
          <div className="mt-4 bg-white bg-opacity-10 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="text-white">
                <h3 className="text-lg font-medium">{image.filename}</h3>
                <p className="text-sm opacity-75">
                  {new Date(image.created_at).toLocaleString()}
                </p>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={handleDownload}
                  className="bg-white text-gray-800 rounded-md px-4 py-2 hover:bg-gray-100 transition-colors"
                >
                  Download
                </button>
              </div>
            </div>

            {showMetadata && (
              <div className="mt-4 grid grid-cols-2 gap-4 text-sm text-white">
                <div>
                  <p className="font-medium">Dimensions</p>
                  <p className="opacity-75">
                    {image.width} × {image.height} pixels
                  </p>
                </div>
                <div>
                  <p className="font-medium">Size</p>
                  <p className="opacity-75">
                    {(image.size_bytes / 1024).toFixed(1)} KB
                  </p>
                </div>
                <div>
                  <p className="font-medium">Type</p>
                  <p className="opacity-75">{image.mime_type}</p>
                </div>
                {image.dpi && (
                  <div>
                    <p className="font-medium">DPI</p>
                    <p className="opacity-75">{image.dpi}</p>
                  </div>
                )}
                {image.color_space && (
                  <div>
                    <p className="font-medium">Color Space</p>
                    <p className="opacity-75">{image.color_space}</p>
                  </div>
                )}
                {image.tags.length > 0 && (
                  <div className="col-span-2">
                    <p className="font-medium">Tags</p>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {image.tags.map((tag) => (
                        <span
                          key={tag}
                          className="bg-white bg-opacity-20 rounded-full px-2 py-1 text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

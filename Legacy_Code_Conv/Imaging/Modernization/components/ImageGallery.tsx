/**
 * Image gallery component with filtering and search.
 */
import React, { useState, useEffect } from 'react';
import { ImageMetadata, ImageSearchQuery } from '../types';
import { ImagePreview } from './ImagePreview';
import { Pagination } from './Pagination';
import { SearchFilter } from './SearchFilter';

interface ImageGalleryProps {
  companyId: string;
  onSelect?: (image: ImageMetadata) => void;
  onDelete?: (image: ImageMetadata) => void;
  pageSize?: number;
}

export const ImageGallery: React.FC<ImageGalleryProps> = ({
  companyId,
  onSelect,
  onDelete,
  pageSize = 20,
}) => {
  const [images, setImages] = useState<ImageMetadata[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [totalImages, setTotalImages] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<ImageSearchQuery>({
    company_id: companyId,
    page: 1,
    page_size: pageSize,
  });

  const fetchImages = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/imaging/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchQuery),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch images');
      }

      const data = await response.json();
      setImages(data.results);
      setTotalImages(data.total);
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchImages();
  }, [searchQuery]);

  const handleSearch = (query: Partial<ImageSearchQuery>) => {
    setSearchQuery({
      ...searchQuery,
      ...query,
      page: 1, // Reset to first page on new search
    });
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    setSearchQuery({
      ...searchQuery,
      page,
    });
  };

  const handleDelete = async (image: ImageMetadata) => {
    if (!onDelete || !window.confirm('Are you sure you want to delete this image?')) {
      return;
    }

    try {
      const response = await fetch(`/api/imaging/${image.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete image');
      }

      onDelete(image);
      fetchImages(); // Refresh the gallery
    } catch (error) {
      console.error('Failed to delete image:', error);
    }
  };

  if (error) {
    return (
      <div className="text-center text-red-600 p-4">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <SearchFilter
        onSearch={handleSearch}
        loading={loading}
      />

      {loading ? (
        <div className="text-center p-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
          <p className="mt-2 text-gray-600">Loading images...</p>
        </div>
      ) : (
        <>
          {images.length === 0 ? (
            <div className="text-center text-gray-500 p-8">
              No images found
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {images.map((image) => (
                <div
                  key={image.id}
                  className="relative group"
                >
                  <div
                    className="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-lg bg-gray-200"
                    onClick={() => onSelect?.(image)}
                  >
                    <ImagePreview
                      src={image.url}
                      alt={image.filename}
                      className="object-cover cursor-pointer transform transition-transform group-hover:scale-105"
                    />
                  </div>
                  
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity flex items-center justify-center opacity-0 group-hover:opacity-100">
                    <button
                      onClick={() => onSelect?.(image)}
                      className="bg-white text-gray-800 rounded-full p-2 mx-1 hover:bg-blue-500 hover:text-white transition-colors"
                    >
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    
                    {onDelete && (
                      <button
                        onClick={() => handleDelete(image)}
                        className="bg-white text-gray-800 rounded-full p-2 mx-1 hover:bg-red-500 hover:text-white transition-colors"
                      >
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    )}
                  </div>

                  <div className="mt-2">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {image.filename}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(image.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          <Pagination
            currentPage={currentPage}
            totalItems={totalImages}
            pageSize={pageSize}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  );
};

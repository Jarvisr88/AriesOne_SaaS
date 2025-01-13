import React, { useState } from 'react';
import type { Address } from '../../types/address';

interface MapButtonProps {
  address?: Address;
  className?: string;
}

interface MapProvider {
  id: string;
  name: string;
  icon: string;
}

export const MapButton: React.FC<MapButtonProps> = ({
  address,
  className,
}) => {
  const [providers, setProviders] = useState<MapProvider[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>();

  const loadProviders = async () => {
    try {
      setIsLoading(true);
      setError(undefined);
      
      const response = await fetch('/api/controls/map/providers');
      const data = await response.json();
      
      setProviders(data.map((id: string) => ({
        id,
        name: id.charAt(0).toUpperCase() + id.slice(1),
        icon: `/icons/maps/${id}.svg`,
      })));
    } catch (error) {
      console.error('Failed to load map providers:', error);
      setError('Failed to load map providers');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMapClick = async (provider: MapProvider) => {
    if (!address) return;

    try {
      setIsLoading(true);
      setError(undefined);
      
      const response = await fetch('/api/controls/address/geocode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address,
          provider: provider.id,
        }),
      });
      
      const { latitude, longitude } = await response.json();
      
      // Open in new tab
      window.open(
        `https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`,
        '_blank'
      );
    } catch (error) {
      console.error('Failed to geocode address:', error);
      setError('Failed to open map');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={loadProviders}
        disabled={!address || isLoading}
        className={className}
      >
        <span className="flex items-center space-x-2">
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
            />
          </svg>
          <span>Map</span>
        </span>
      </button>

      {providers.length > 0 && (
        <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
          <div className="py-1" role="menu">
            {providers.map(provider => (
              <button
                key={provider.id}
                onClick={() => handleMapClick(provider)}
                className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                role="menuitem"
              >
                <span className="flex items-center space-x-2">
                  <img
                    src={provider.icon}
                    alt=""
                    className="h-4 w-4"
                  />
                  <span>{provider.name}</span>
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="absolute right-0 mt-2 w-48 rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

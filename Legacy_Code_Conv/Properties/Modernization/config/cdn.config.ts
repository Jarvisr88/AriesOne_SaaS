interface CDNConfig {
  baseUrl: string;
  region: string;
  cacheDuration: number;
  preloadEnabled: boolean;
  preloadPatterns: string[];
}

export const cdnConfig: CDNConfig = {
  baseUrl: process.env.NEXT_PUBLIC_CDN_URL || '/assets',
  region: process.env.NEXT_PUBLIC_CDN_REGION || 'us-east-1',
  cacheDuration: 24 * 60 * 60, // 24 hours in seconds
  preloadEnabled: true,
  preloadPatterns: [
    'checked',
    'unchecked',
    'indeterminate',
    'reload',
    'reload2'
  ]
};

export const cacheConfig = {
  maxAge: 24 * 60 * 60 * 1000, // 24 hours in milliseconds
  maxSize: 100, // Maximum number of cached items
  staleWhileRevalidate: 60 * 60 * 1000 // 1 hour in milliseconds
};

export const cdnHeaders = {
  'Cache-Control': `public, max-age=${cdnConfig.cacheDuration}, stale-while-revalidate=3600`,
  'Content-Type': 'image/svg+xml',
  'Access-Control-Allow-Origin': '*'
};

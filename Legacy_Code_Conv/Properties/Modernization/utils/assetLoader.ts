interface CacheConfig {
  maxAge: number;
  maxSize: number;
}

class AssetCache {
  private cache: Map<string, { data: string; timestamp: number }>;
  private maxAge: number;
  private maxSize: number;

  constructor({ maxAge, maxSize }: CacheConfig) {
    this.cache = new Map();
    this.maxAge = maxAge;
    this.maxSize = maxSize;
  }

  get(key: string): string | null {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > this.maxAge) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  set(key: string, value: string): void {
    // Clean up old entries if cache is full
    if (this.cache.size >= this.maxSize) {
      const oldestKey = Array.from(this.cache.entries())
        .sort(([, a], [, b]) => a.timestamp - b.timestamp)[0][0];
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      data: value,
      timestamp: Date.now()
    });
  }

  clear(): void {
    this.cache.clear();
  }
}

const iconCache = new AssetCache({
  maxAge: 24 * 60 * 60 * 1000, // 24 hours
  maxSize: 100 // Maximum number of cached icons
});

export async function loadIcon(
  name: string,
  theme: 'light' | 'dark',
  baseUrl: string
): Promise<string> {
  const cacheKey = `${name}-${theme}`;
  const cachedIcon = iconCache.get(cacheKey);
  
  if (cachedIcon) {
    return cachedIcon;
  }

  try {
    const response = await fetch(`${baseUrl}/${theme}/${name}.svg`);
    if (!response.ok) {
      throw new Error(`Failed to load icon: ${name}`);
    }

    const iconData = await response.text();
    iconCache.set(cacheKey, iconData);
    return iconData;
  } catch (error) {
    console.error(`Error loading icon ${name}:`, error);
    throw error;
  }
}

export function preloadIcon(
  name: string,
  theme: 'light' | 'dark',
  baseUrl: string
): void {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.as = 'image';
  link.href = `${baseUrl}/${theme}/${name}.svg`;
  document.head.appendChild(link);
}

export function preloadCommonIcons(baseUrl: string): void {
  const commonIcons = ['checked', 'unchecked', 'reload'];
  const themes: Array<'light' | 'dark'> = ['light', 'dark'];

  commonIcons.forEach(icon => {
    themes.forEach(theme => {
      preloadIcon(icon, theme, baseUrl);
    });
  });
}

export function clearIconCache(): void {
  iconCache.clear();
}

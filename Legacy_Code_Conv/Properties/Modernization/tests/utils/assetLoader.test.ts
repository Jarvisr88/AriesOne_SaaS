import { describe, it, expect, beforeEach, vi } from 'vitest';
import { loadIcon, preloadIcon, preloadCommonIcons, clearIconCache } from '../../utils/assetLoader';

describe('Asset Loader', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    clearIconCache();
    vi.spyOn(global, 'fetch');
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  describe('loadIcon', () => {
    it('loads icon from CDN', async () => {
      const mockSvg = '<svg>test</svg>';
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        text: () => Promise.resolve(mockSvg),
      });

      const result = await loadIcon('test-icon', 'light', 'https://cdn.example.com');
      expect(result).toBe(mockSvg);
      expect(fetch).toHaveBeenCalledWith('https://cdn.example.com/light/test-icon.svg');
    });

    it('caches loaded icons', async () => {
      const mockSvg = '<svg>test</svg>';
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        text: () => Promise.resolve(mockSvg),
      });

      await loadIcon('test-icon', 'light', 'https://cdn.example.com');
      await loadIcon('test-icon', 'light', 'https://cdn.example.com');

      expect(fetch).toHaveBeenCalledTimes(1);
    });

    it('handles fetch errors', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      await expect(loadIcon('test-icon', 'light', 'https://cdn.example.com'))
        .rejects.toThrow('Network error');
    });

    it('handles non-ok responses', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
      });

      await expect(loadIcon('test-icon', 'light', 'https://cdn.example.com'))
        .rejects.toThrow('Failed to load icon: test-icon');
    });
  });

  describe('preloadIcon', () => {
    it('adds preload link to document head', () => {
      const appendChildSpy = vi.spyOn(document.head, 'appendChild');
      
      preloadIcon('test-icon', 'light', 'https://cdn.example.com');

      expect(appendChildSpy).toHaveBeenCalledTimes(1);
      const link = appendChildSpy.mock.calls[0][0] as HTMLLinkElement;
      expect(link.rel).toBe('preload');
      expect(link.as).toBe('image');
      expect(link.href).toBe('https://cdn.example.com/light/test-icon.svg');
    });
  });

  describe('preloadCommonIcons', () => {
    it('preloads all common icons for both themes', () => {
      const appendChildSpy = vi.spyOn(document.head, 'appendChild');
      
      preloadCommonIcons('https://cdn.example.com');

      // 3 common icons * 2 themes = 6 preload links
      expect(appendChildSpy).toHaveBeenCalledTimes(6);
    });
  });

  describe('Cache Management', () => {
    it('clears cache when clearIconCache is called', async () => {
      const mockSvg = '<svg>test</svg>';
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        text: () => Promise.resolve(mockSvg),
      });

      await loadIcon('test-icon', 'light', 'https://cdn.example.com');
      clearIconCache();
      await loadIcon('test-icon', 'light', 'https://cdn.example.com');

      expect(fetch).toHaveBeenCalledTimes(2);
    });
  });
});

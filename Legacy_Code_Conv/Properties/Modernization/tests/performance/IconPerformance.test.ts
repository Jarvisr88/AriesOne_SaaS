import { describe, it, expect, beforeEach, vi } from 'vitest';
import { loadIcon, clearIconCache } from '../../utils/assetLoader';

describe('Icon System Performance', () => {
  beforeEach(() => {
    clearIconCache();
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('loads icons within performance budget', async () => {
    const mockSvg = '<svg>test</svg>';
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      text: () => Promise.resolve(mockSvg),
    });

    const start = performance.now();
    await loadIcon('test-icon', 'light', 'https://cdn.example.com');
    const end = performance.now();

    const loadTime = end - start;
    expect(loadTime).toBeLessThan(100); // 100ms budget
  });

  it('caches improve subsequent load times', async () => {
    const mockSvg = '<svg>test</svg>';
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      text: () => Promise.resolve(mockSvg),
    });

    // First load
    const start1 = performance.now();
    await loadIcon('test-icon', 'light', 'https://cdn.example.com');
    const end1 = performance.now();
    const firstLoadTime = end1 - start1;

    // Second load (should be from cache)
    const start2 = performance.now();
    await loadIcon('test-icon', 'light', 'https://cdn.example.com');
    const end2 = performance.now();
    const secondLoadTime = end2 - start2;

    expect(secondLoadTime).toBeLessThan(firstLoadTime);
    expect(secondLoadTime).toBeLessThan(10); // 10ms budget for cached loads
  });

  it('handles concurrent requests efficiently', async () => {
    const mockSvg = '<svg>test</svg>';
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      text: () => Promise.resolve(mockSvg),
    });

    const start = performance.now();
    await Promise.all([
      loadIcon('icon1', 'light', 'https://cdn.example.com'),
      loadIcon('icon2', 'light', 'https://cdn.example.com'),
      loadIcon('icon3', 'light', 'https://cdn.example.com'),
    ]);
    const end = performance.now();

    const totalTime = end - start;
    expect(totalTime).toBeLessThan(300); // 300ms budget for 3 concurrent loads
  });

  it('maintains performance under memory pressure', async () => {
    const mockSvg = '<svg>test</svg>';
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      text: () => Promise.resolve(mockSvg),
    });

    // Simulate loading many icons
    const loadTimes: number[] = [];
    for (let i = 0; i < 100; i++) {
      const start = performance.now();
      await loadIcon(`icon${i}`, 'light', 'https://cdn.example.com');
      const end = performance.now();
      loadTimes.push(end - start);
    }

    // Check if later loads are still performant
    const averageLoadTime = loadTimes.reduce((a, b) => a + b) / loadTimes.length;
    expect(averageLoadTime).toBeLessThan(50); // 50ms average budget

    // Check if last loads are still performant
    const lastTenLoadTimes = loadTimes.slice(-10);
    const averageLastTenLoadTime = lastTenLoadTimes.reduce((a, b) => a + b) / 10;
    expect(averageLastTenLoadTime).toBeLessThan(50); // Should still be fast
  });
});

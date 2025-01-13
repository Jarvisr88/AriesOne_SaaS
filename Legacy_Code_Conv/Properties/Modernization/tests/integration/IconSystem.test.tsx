import React from 'react';
import { render, act, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { IconProvider } from '../../components/IconProvider';
import { LazyIcon } from '../../components/LazyIcon';
import { loadIcon } from '../../utils/assetLoader';

vi.mock('../../utils/assetLoader', () => ({
  loadIcon: vi.fn(),
}));

describe('Icon System Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    document.documentElement.classList.remove('dark');
  });

  it('loads and renders icons through the provider system', async () => {
    const mockSvg = '<svg><path d="M1 1" /></svg>';
    (loadIcon as any).mockResolvedValue(mockSvg);

    render(
      <IconProvider cdnUrl="https://cdn.example.com">
        <LazyIcon name="test-icon" data-testid="test-icon" />
      </IconProvider>
    );

    // Should show loading state initially
    expect(screen.getByTestId('test-icon')).toHaveClass('animate-pulse');

    // Wait for icon to load
    await waitFor(() => {
      expect(screen.getByTestId('test-icon')).not.toHaveClass('animate-pulse');
    });

    expect(loadIcon).toHaveBeenCalledWith(
      'test-icon',
      'light',
      'https://cdn.example.com'
    );
  });

  it('handles theme changes correctly', async () => {
    const mockSvg = '<svg><path d="M1 1" /></svg>';
    (loadIcon as any).mockResolvedValue(mockSvg);

    render(
      <IconProvider cdnUrl="https://cdn.example.com">
        <LazyIcon name="test-icon" data-testid="test-icon" />
      </IconProvider>
    );

    await waitFor(() => {
      expect(loadIcon).toHaveBeenCalledWith(
        'test-icon',
        'light',
        'https://cdn.example.com'
      );
    });

    // Simulate dark mode change
    act(() => {
      document.documentElement.classList.add('dark');
      window.dispatchEvent(new Event('storage'));
    });

    await waitFor(() => {
      expect(loadIcon).toHaveBeenCalledWith(
        'test-icon',
        'dark',
        'https://cdn.example.com'
      );
    });
  });

  it('handles loading errors gracefully', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    (loadIcon as any).mockRejectedValue(new Error('Failed to load'));

    render(
      <IconProvider cdnUrl="https://cdn.example.com">
        <LazyIcon
          name="test-icon"
          data-testid="test-icon"
          fallback={<div data-testid="fallback">Error</div>}
        />
      </IconProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('fallback')).toBeInTheDocument();
    });

    expect(consoleError).toHaveBeenCalled();
  });

  it('applies custom styling correctly', async () => {
    const mockSvg = '<svg><path d="M1 1" /></svg>';
    (loadIcon as any).mockResolvedValue(mockSvg);

    render(
      <IconProvider cdnUrl="https://cdn.example.com">
        <LazyIcon
          name="test-icon"
          className="custom-class"
          size={32}
          data-testid="test-icon"
        />
      </IconProvider>
    );

    await waitFor(() => {
      const icon = screen.getByTestId('test-icon');
      expect(icon).toHaveStyle({ width: '32px', height: '32px' });
      expect(icon.innerHTML).toContain('custom-class');
    });
  });
});

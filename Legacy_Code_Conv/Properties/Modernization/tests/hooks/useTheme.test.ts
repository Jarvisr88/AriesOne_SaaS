import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useTheme } from '../../hooks/useTheme';

describe('useTheme Hook', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    document.documentElement.classList.remove('dark');
  });

  it('returns default theme as system', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe('system');
  });

  it('loads theme from localStorage', () => {
    localStorage.getItem = vi.fn().mockReturnValue('dark');
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe('dark');
  });

  it('updates theme when setTheme is called', () => {
    const { result } = renderHook(() => useTheme());
    
    act(() => {
      result.current.setTheme('dark');
    });

    expect(result.current.theme).toBe('dark');
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
  });

  it('responds to system theme changes', () => {
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const { result } = renderHook(() => useTheme());

    act(() => {
      Object.defineProperty(darkModeMediaQuery, 'matches', {
        writable: true,
        value: true,
      });
      darkModeMediaQuery.dispatchEvent(new Event('change'));
    });

    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('persists theme in localStorage', () => {
    const { result } = renderHook(() => useTheme());
    
    act(() => {
      result.current.setTheme('light');
    });

    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light');
  });

  it('correctly identifies dark mode', () => {
    document.documentElement.classList.add('dark');
    const { result } = renderHook(() => useTheme());
    expect(result.current.isDark).toBe(true);
  });
});

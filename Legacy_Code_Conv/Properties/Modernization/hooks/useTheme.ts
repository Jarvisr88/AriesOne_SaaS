import { useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    // Get stored theme or default to system
    return (localStorage.getItem('theme') as Theme) || 'system';
  });

  // Update theme when system preference changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = () => {
      if (theme === 'system') {
        document.documentElement.classList.toggle('dark', mediaQuery.matches);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  // Update theme when it changes
  useEffect(() => {
    const isDark = theme === 'dark' || 
      (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

    document.documentElement.classList.toggle('dark', isDark);
    localStorage.setItem('theme', theme);
  }, [theme]);

  return {
    theme,
    setTheme,
    isDark: document.documentElement.classList.contains('dark'),
  };
}

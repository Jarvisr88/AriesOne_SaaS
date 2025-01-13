import React, { createContext, useContext, useMemo } from 'react';
import { useTheme } from '../hooks/useTheme';

interface IconContextType {
  baseUrl: string;
  theme: 'light' | 'dark' | 'system';
  isDark: boolean;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

const IconContext = createContext<IconContextType | undefined>(undefined);

interface IconProviderProps {
  children: React.ReactNode;
  cdnUrl?: string;
}

export function IconProvider({ 
  children, 
  cdnUrl = process.env.NEXT_PUBLIC_CDN_URL || '/assets/icons'
}: IconProviderProps) {
  const { theme, setTheme, isDark } = useTheme();

  const value = useMemo(() => ({
    baseUrl: cdnUrl,
    theme,
    isDark,
    setTheme
  }), [cdnUrl, theme, isDark]);

  return (
    <IconContext.Provider value={value}>
      {children}
    </IconContext.Provider>
  );
}

export function useIconContext() {
  const context = useContext(IconContext);
  if (context === undefined) {
    throw new Error('useIconContext must be used within an IconProvider');
  }
  return context;
}

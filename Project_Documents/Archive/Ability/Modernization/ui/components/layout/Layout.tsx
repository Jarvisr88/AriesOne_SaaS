import React from 'react';
import { create } from 'zustand';
import { cn } from '../../utils/cn';

interface LayoutState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useLayoutStore = create<LayoutState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}));

interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}

export const Layout: React.FC<LayoutProps> = ({ children, className }) => {
  const sidebarOpen = useLayoutStore((state) => state.sidebarOpen);

  return (
    <div className="min-h-screen bg-background">
      <main
        className={cn(
          'flex-1 transition-all duration-200 ease-in-out',
          sidebarOpen ? 'ml-64' : 'ml-0',
          className
        )}
      >
        {children}
      </main>
    </div>
  );
};

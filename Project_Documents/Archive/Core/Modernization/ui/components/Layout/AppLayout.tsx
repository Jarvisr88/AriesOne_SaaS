import React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { cn } from '../../utils/cn';
import { useStore } from '../../store/store';

interface AppLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export function AppLayout({ children, className }: AppLayoutProps) {
  const { isSidebarOpen } = useStore();

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="flex">
        <Sidebar />
        <main
          className={cn(
            'flex-1 transition-all duration-300 ease-in-out',
            isSidebarOpen ? 'ml-64' : 'ml-20',
            className
          )}
        >
          <div className="container mx-auto p-6">{children}</div>
        </main>
      </div>
    </div>
  );
}

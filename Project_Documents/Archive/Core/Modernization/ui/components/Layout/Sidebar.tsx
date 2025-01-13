import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import {
  Calendar,
  LayoutDashboard,
  FileText,
  Users,
  Settings,
  ChevronRight,
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { Button } from '../Input/Button';
import { useStore } from '../../store/store';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '../Overlay/Tooltip';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Calendar', href: '/calendar', icon: Calendar },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Users', href: '/users', icon: Users },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const location = useLocation();
  const { isSidebarOpen, toggleSidebar } = useStore();

  return (
    <aside
      className={cn(
        'fixed left-0 top-14 z-30 h-[calc(100vh-3.5rem)] w-64 border-r bg-background transition-all duration-300 ease-in-out',
        !isSidebarOpen && 'w-20'
      )}
    >
      <div className="flex h-full flex-col">
        <div className="flex-1 space-y-1 p-3">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <div key={item.name} className="relative">
                {!isSidebarOpen ? (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Link
                        to={item.href}
                        className={cn(
                          'group flex h-10 w-full items-center justify-center rounded-md px-3 text-sm font-medium hover:bg-accent hover:text-accent-foreground',
                          isActive &&
                            'bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground'
                        )}
                      >
                        <item.icon className="h-5 w-5" />
                      </Link>
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      {item.name}
                    </TooltipContent>
                  </Tooltip>
                ) : (
                  <Link
                    to={item.href}
                    className={cn(
                      'group flex h-10 w-full items-center rounded-md px-3 text-sm font-medium hover:bg-accent hover:text-accent-foreground',
                      isActive &&
                        'bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground'
                    )}
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                )}
              </div>
            );
          })}
        </div>
        <div className="border-t p-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="w-full justify-center"
          >
            <ChevronRight
              className={cn(
                'h-4 w-4 transition-transform',
                !isSidebarOpen && 'rotate-180'
              )}
            />
          </Button>
        </div>
      </div>
    </aside>
  );
}

import React from 'react';
import { Bell, Settings, User } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../Navigation/DropdownMenu';
import { Button } from '../Input/Button';
import { useAuth } from '../../hooks/use-auth';
import { useTheme } from '../../hooks/use-theme';
import { ThemeToggle } from '../Theme/ThemeToggle';

export function Header() {
  const { user, signOut } = useAuth();
  const { theme } = useTheme();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <a className="mr-6 flex items-center space-x-2" href="/">
            <img
              src={theme === 'dark' ? '/logo-dark.svg' : '/logo-light.svg'}
              alt="AriesOne Logo"
              className="h-6 w-6"
            />
            <span className="hidden font-bold sm:inline-block">
              AriesOne
            </span>
          </a>
        </div>

        <div className="flex flex-1 items-center justify-end space-x-4">
          <Button variant="ghost" size="icon">
            <Bell className="h-4 w-4" />
          </Button>
          <ThemeToggle />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="relative h-8 w-8 rounded-full"
              >
                <User className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => signOut()}>
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}

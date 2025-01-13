import React from 'react';
import { Button } from '../core/Button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../core/Select';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { cn } from '../../utils/cn';
import { Views } from 'react-big-calendar';

interface CalendarToolbarProps {
  view: keyof typeof Views;
  views: (keyof typeof Views)[];
  label: string;
  onView: (view: keyof typeof Views) => void;
  onNavigate: (action: 'PREV' | 'NEXT' | 'TODAY') => void;
  onAddEvent?: () => void;
  className?: string;
}

export function CalendarToolbar({
  view,
  views,
  label,
  onView,
  onNavigate,
  onAddEvent,
  className,
}: CalendarToolbarProps) {
  const viewOptions = {
    month: 'Month',
    week: 'Week',
    day: 'Day',
    agenda: 'Agenda',
  };

  return (
    <div
      className={cn(
        'mb-4 flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-x-4 sm:space-y-0',
        className
      )}
    >
      <div className="flex items-center space-x-4">
        <Button
          variant="outline"
          size="icon"
          onClick={() => onNavigate('PREV')}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onNavigate('TODAY')}
        >
          Today
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={() => onNavigate('NEXT')}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
        <span className="text-sm font-medium">{label}</span>
      </div>
      <div className="flex items-center space-x-4">
        <Select
          value={view}
          onValueChange={(value) => onView(value as keyof typeof Views)}
        >
          <SelectTrigger className="w-[120px]">
            <SelectValue placeholder="Select view" />
          </SelectTrigger>
          <SelectContent>
            {views.map((viewKey) => (
              <SelectItem key={viewKey} value={viewKey}>
                {viewOptions[viewKey]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {onAddEvent && (
          <Button onClick={onAddEvent}>
            <Plus className="mr-2 h-4 w-4" />
            Add Event
          </Button>
        )}
      </div>
    </div>
  );
}

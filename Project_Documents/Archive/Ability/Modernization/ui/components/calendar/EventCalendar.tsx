import React, { useMemo } from 'react';
import {
  Calendar,
  Views,
  DateLocalizer,
  momentLocalizer,
} from 'react-big-calendar';
import moment from 'moment-timezone';
import { cn } from '../../utils/cn';
import { useTheme } from '../../hooks/use-theme';

const localizer = momentLocalizer(moment);

export interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  allDay?: boolean;
  resource?: any;
}

interface EventCalendarProps {
  events: CalendarEvent[];
  localizer?: DateLocalizer;
  defaultView?: keyof typeof Views;
  onSelectEvent?: (event: CalendarEvent) => void;
  onSelectSlot?: (slotInfo: any) => void;
  className?: string;
}

export function EventCalendar({
  events,
  localizer: userLocalizer,
  defaultView = 'month',
  onSelectEvent,
  onSelectSlot,
  className,
}: EventCalendarProps) {
  const { theme } = useTheme();

  const calendarLocalizer = useMemo(
    () => userLocalizer || localizer,
    [userLocalizer]
  );

  return (
    <div
      className={cn(
        'h-[700px] rounded-md border bg-background p-4',
        className
      )}
    >
      <Calendar
        localizer={calendarLocalizer}
        events={events}
        defaultView={defaultView}
        startAccessor="start"
        endAccessor="end"
        selectable
        onSelectEvent={onSelectEvent}
        onSelectSlot={onSelectSlot}
        views={['month', 'week', 'day', 'agenda']}
        className={cn(
          'h-full',
          theme === 'dark' && 'rbc-calendar-dark'
        )}
        formats={{
          timeGutterFormat: 'HH:mm',
          eventTimeRangeFormat: ({ start, end }: any) =>
            `${moment(start).format('HH:mm')} - ${moment(end).format('HH:mm')}`,
          agendaTimeRangeFormat: ({ start, end }: any) =>
            `${moment(start).format('HH:mm')} - ${moment(end).format('HH:mm')}`,
        }}
      />
    </div>
  );
}

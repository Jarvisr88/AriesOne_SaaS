import React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { Button } from '../core/Button';
import { Input } from '../core/Input';
import { X } from 'lucide-react';
import { CalendarEvent } from './EventCalendar';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const eventSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  start: z.string().min(1, 'Start time is required'),
  end: z.string().min(1, 'End time is required'),
  allDay: z.boolean().optional(),
  description: z.string().optional(),
});

type EventFormData = z.infer<typeof eventSchema>;

interface EventDialogProps {
  event?: CalendarEvent;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (event: EventFormData) => void;
  onDelete?: () => void;
}

export function EventDialog({
  event,
  open,
  onOpenChange,
  onSave,
  onDelete,
}: EventDialogProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<EventFormData>({
    resolver: zodResolver(eventSchema),
    defaultValues: event
      ? {
          title: event.title,
          start: event.start.toISOString().slice(0, 16),
          end: event.end.toISOString().slice(0, 16),
          allDay: event.allDay,
        }
      : undefined,
  });

  const onSubmit = (data: EventFormData) => {
    onSave(data);
    onOpenChange(false);
    reset();
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] max-h-[85vh] w-[90vw] max-w-[450px] translate-x-[-50%] translate-y-[-50%] rounded-md bg-background p-6 shadow-lg">
          <Dialog.Title className="text-lg font-semibold">
            {event ? 'Edit Event' : 'New Event'}
          </Dialog.Title>
          <form onSubmit={handleSubmit(onSubmit)} className="mt-4 space-y-4">
            <div className="space-y-2">
              <label
                htmlFor="title"
                className="text-sm font-medium text-foreground"
              >
                Title
              </label>
              <Input
                id="title"
                {...register('title')}
                error={!!errors.title}
                helperText={errors.title?.message}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label
                  htmlFor="start"
                  className="text-sm font-medium text-foreground"
                >
                  Start
                </label>
                <Input
                  id="start"
                  type="datetime-local"
                  {...register('start')}
                  error={!!errors.start}
                  helperText={errors.start?.message}
                />
              </div>
              <div className="space-y-2">
                <label
                  htmlFor="end"
                  className="text-sm font-medium text-foreground"
                >
                  End
                </label>
                <Input
                  id="end"
                  type="datetime-local"
                  {...register('end')}
                  error={!!errors.end}
                  helperText={errors.end?.message}
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="allDay"
                {...register('allDay')}
                className="h-4 w-4 rounded border-input"
              />
              <label
                htmlFor="allDay"
                className="text-sm font-medium text-foreground"
              >
                All day
              </label>
            </div>
            <div className="space-y-2">
              <label
                htmlFor="description"
                className="text-sm font-medium text-foreground"
              >
                Description
              </label>
              <textarea
                id="description"
                {...register('description')}
                className="h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
            <div className="flex justify-end space-x-2">
              {event && onDelete && (
                <Button
                  type="button"
                  variant="destructive"
                  onClick={onDelete}
                >
                  Delete
                </Button>
              )}
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit">Save</Button>
            </div>
          </form>
          <Dialog.Close asChild>
            <button
              className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              aria-label="Close"
            >
              <X className="h-4 w-4" />
            </button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

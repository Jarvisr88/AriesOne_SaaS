import { z } from "zod";

// Calendar event schema for validation
export const calendarEventSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
  startDate: z.date(),
  endDate: z.date(),
  location: z.string().optional(),
  attendees: z.array(z.string().email("Invalid email address")),
  reminders: z.array(z.object({
    method: z.enum(["email", "popup"]),
    minutes: z.number().min(0)
  })),
  isAllDay: z.boolean(),
  recurrence: z.object({
    frequency: z.enum(["none", "daily", "weekly", "monthly", "yearly"]),
    interval: z.number().min(1),
    until: z.date().optional(),
    count: z.number().min(1).optional()
  }).optional()
});

// Infer TypeScript types from schema
export type CalendarEvent = z.infer<typeof calendarEventSchema>;

export interface CalendarEventDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (event: CalendarEvent) => Promise<void>;
  defaultValues?: Partial<CalendarEvent>;
}

export interface ReminderOption {
  label: string;
  value: number;
  method: "email" | "popup";
}

export interface RecurrenceOption {
  label: string;
  value: "none" | "daily" | "weekly" | "monthly" | "yearly";
}

export const DEFAULT_REMINDERS: ReminderOption[] = [
  { label: "10 minutes before", value: 10, method: "popup" },
  { label: "30 minutes before", value: 30, method: "popup" },
  { label: "1 hour before", value: 60, method: "email" },
  { label: "1 day before", value: 1440, method: "email" }
];

export const RECURRENCE_OPTIONS: RecurrenceOption[] = [
  { label: "Does not repeat", value: "none" },
  { label: "Daily", value: "daily" },
  { label: "Weekly", value: "weekly" },
  { label: "Monthly", value: "monthly" },
  { label: "Yearly", value: "yearly" }
];

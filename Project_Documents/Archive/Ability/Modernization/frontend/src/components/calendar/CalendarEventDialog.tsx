import React from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { format } from "date-fns";
import { CalendarIcon, X } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

import {
  CalendarEvent,
  CalendarEventDialogProps,
  calendarEventSchema,
  DEFAULT_REMINDERS,
  RECURRENCE_OPTIONS,
} from "@/types/calendar";

export function CalendarEventDialog({
  isOpen,
  onClose,
  onSubmit,
  defaultValues,
}: CalendarEventDialogProps) {
  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<CalendarEvent>({
    resolver: zodResolver(calendarEventSchema),
    defaultValues: {
      title: "",
      description: "",
      startDate: new Date(),
      endDate: new Date(),
      location: "",
      attendees: [],
      reminders: [DEFAULT_REMINDERS[0]],
      isAllDay: false,
      ...defaultValues,
    },
  });

  const isAllDay = watch("isAllDay");

  const handleFormSubmit = async (data: CalendarEvent) => {
    try {
      await onSubmit(data);
      onClose();
    } catch (error) {
      console.error("Failed to create calendar event:", error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create Calendar Event</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
          <div className="grid gap-4">
            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                {...register("title")}
                placeholder="Event title"
                className={errors.title ? "border-red-500" : ""}
              />
              {errors.title && (
                <p className="text-sm text-red-500">{errors.title.message}</p>
              )}
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                {...register("description")}
                placeholder="Event description"
                rows={3}
              />
            </div>

            {/* Date and Time */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Start</Label>
                <Controller
                  name="startDate"
                  control={control}
                  render={({ field }) => (
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={`w-full justify-start text-left font-normal ${
                            errors.startDate ? "border-red-500" : ""
                          }`}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {format(field.value, isAllDay ? "PPP" : "PPP p")}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={field.value}
                          onSelect={field.onChange}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  )}
                />
              </div>

              <div className="space-y-2">
                <Label>End</Label>
                <Controller
                  name="endDate"
                  control={control}
                  render={({ field }) => (
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={`w-full justify-start text-left font-normal ${
                            errors.endDate ? "border-red-500" : ""
                          }`}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {format(field.value, isAllDay ? "PPP" : "PPP p")}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={field.value}
                          onSelect={field.onChange}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  )}
                />
              </div>
            </div>

            {/* All Day Switch */}
            <div className="flex items-center space-x-2">
              <Controller
                name="isAllDay"
                control={control}
                render={({ field }) => (
                  <Switch
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                )}
              />
              <Label>All day</Label>
            </div>

            {/* Location */}
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                {...register("location")}
                placeholder="Add location"
              />
            </div>

            {/* Attendees */}
            <div className="space-y-2">
              <Label htmlFor="attendees">Attendees</Label>
              <div className="flex flex-wrap gap-2">
                <Controller
                  name="attendees"
                  control={control}
                  render={({ field }) => (
                    <>
                      {field.value.map((email, index) => (
                        <Badge key={index} variant="secondary">
                          {email}
                          <X
                            className="ml-1 h-3 w-3 cursor-pointer"
                            onClick={() => {
                              const newAttendees = [...field.value];
                              newAttendees.splice(index, 1);
                              field.onChange(newAttendees);
                            }}
                          />
                        </Badge>
                      ))}
                      <Input
                        type="email"
                        placeholder="Add attendee email"
                        className="w-full"
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            e.preventDefault();
                            const input = e.target as HTMLInputElement;
                            const email = input.value.trim();
                            if (email && !field.value.includes(email)) {
                              field.onChange([...field.value, email]);
                              input.value = "";
                            }
                          }
                        }}
                      />
                    </>
                  )}
                />
              </div>
            </div>

            {/* Reminders */}
            <div className="space-y-2">
              <Label>Reminders</Label>
              <Controller
                name="reminders"
                control={control}
                render={({ field }) => (
                  <Select
                    value={field.value[0]?.minutes.toString()}
                    onValueChange={(value) => {
                      const reminder = DEFAULT_REMINDERS.find(
                        (r) => r.value.toString() === value
                      );
                      if (reminder) {
                        field.onChange([reminder]);
                      }
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select reminder" />
                    </SelectTrigger>
                    <SelectContent>
                      {DEFAULT_REMINDERS.map((reminder) => (
                        <SelectItem
                          key={reminder.value}
                          value={reminder.value.toString()}
                        >
                          {reminder.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            </div>

            {/* Recurrence */}
            <div className="space-y-2">
              <Label>Repeat</Label>
              <Controller
                name="recurrence.frequency"
                control={control}
                defaultValue="none"
                render={({ field }) => (
                  <Select
                    value={field.value}
                    onValueChange={field.onChange}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select frequency" />
                    </SelectTrigger>
                    <SelectContent>
                      {RECURRENCE_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create Event"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

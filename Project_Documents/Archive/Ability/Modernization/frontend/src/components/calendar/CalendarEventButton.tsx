import React from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CalendarEventDialog } from "./CalendarEventDialog";
import { useCalendarDialog } from "@/hooks/useCalendarDialog";

export function CalendarEventButton() {
  const { isOpen, isLoading, onOpen, onClose, onSubmit } = useCalendarDialog();

  return (
    <>
      <Button
        onClick={onOpen}
        disabled={isLoading}
        className="flex items-center gap-2"
      >
        <Plus className="h-4 w-4" />
        Create Event
      </Button>

      <CalendarEventDialog
        isOpen={isOpen}
        onClose={onClose}
        onSubmit={onSubmit}
        defaultValues={{
          startDate: new Date(),
          endDate: new Date(Date.now() + 3600000), // 1 hour from now
          reminders: [
            {
              method: "popup",
              minutes: 10,
            },
          ],
        }}
      />
    </>
  );
}

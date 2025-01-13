import { useState, useCallback } from "react";
import { CalendarEvent } from "@/types/calendar";
import { googleCalendarAPI } from "@/lib/google-calendar";
import { useToast } from "@/components/ui/use-toast";

export function useCalendarDialog() {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleOpen = useCallback(() => {
    setIsOpen(true);
  }, []);

  const handleClose = useCallback(() => {
    setIsOpen(false);
  }, []);

  const handleSubmit = useCallback(async (event: CalendarEvent) => {
    setIsLoading(true);
    try {
      // Ensure we're authenticated
      await googleCalendarAPI.authenticate();

      // Create the event
      const eventId = await googleCalendarAPI.createEvent(event);

      toast({
        title: "Event Created",
        description: "Calendar event has been created successfully.",
        variant: "default",
      });

      return eventId;
    } catch (error) {
      console.error("Failed to create calendar event:", error);
      toast({
        title: "Error",
        description: "Failed to create calendar event. Please try again.",
        variant: "destructive",
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  return {
    isOpen,
    isLoading,
    onOpen: handleOpen,
    onClose: handleClose,
    onSubmit: handleSubmit,
  };
}

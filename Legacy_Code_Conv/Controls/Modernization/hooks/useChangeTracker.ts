import { useState, useCallback } from 'react';
import { ChangeType, FieldChange } from '../types/changes';

interface UseChangeTrackerProps {
  controlId: string;
  controlType: string;
  onChanged?: (changes: Record<string, FieldChange>) => void;
}

export const useChangeTracker = ({
  controlId,
  controlType,
  onChanged,
}: UseChangeTrackerProps) => {
  const [changes, setChanges] = useState<Record<string, FieldChange>>({});

  const trackChange = useCallback((
    fieldName: string,
    oldValue: any,
    newValue: any,
    userId?: string
  ) => {
    if (oldValue === newValue) return;

    const changeType = !oldValue 
      ? ChangeType.ADDED 
      : !newValue 
        ? ChangeType.REMOVED 
        : ChangeType.MODIFIED;

    const change: FieldChange = {
      fieldName,
      oldValue,
      newValue,
      changeType,
      timestamp: new Date().toISOString(),
      userId,
    };

    setChanges(prev => {
      const updated = { ...prev, [fieldName]: change };
      onChanged?.(updated);
      return updated;
    });
  }, [onChanged]);

  const hasChanges = useCallback(() => {
    return Object.keys(changes).length > 0;
  }, [changes]);

  const clearChanges = useCallback(() => {
    setChanges({});
    onChanged?.({});
  }, [onChanged]);

  return {
    changes,
    trackChange,
    hasChanges,
    clearChanges,
  };
};

import { useState, useCallback, useEffect } from "react";
import { z } from "zod";
import {
  EntryState,
  EntryConfig,
  EntryValidation,
  EntryFormatter,
  EntryChangeEvent,
} from "@/types/entry";

export function useEntry<T>(config: EntryConfig<T>) {
  const {
    initialValue,
    validation = [],
    formatter,
    schema,
    onChange,
    onValidate,
  } = config;

  const [state, setState] = useState<EntryState<T>>(() => {
    const value = initialValue as T;
    const displayValue = formatter ? formatter.format(value) : String(value);
    return {
      value,
      displayValue,
      isValid: true,
      isDirty: false,
      isTouched: false,
    };
  });

  const validate = useCallback(
    (value: T): { isValid: boolean; error?: string } => {
      // Zod schema validation
      if (schema) {
        try {
          schema.parse(value);
        } catch (error) {
          if (error instanceof z.ZodError) {
            return {
              isValid: false,
              error: error.errors[0].message,
            };
          }
        }
      }

      // Custom validations
      for (const validator of validation) {
        if (!validator.validate(value)) {
          return {
            isValid: false,
            error: validator.message,
          };
        }
      }

      return { isValid: true };
    },
    [schema, validation]
  );

  const handleChange = useCallback(
    (newValue: T | string) => {
      let parsedValue: T;
      let displayValue: string;

      if (formatter) {
        if (typeof newValue === "string") {
          try {
            parsedValue = formatter.parse(newValue);
            displayValue = newValue;
          } catch (error) {
            parsedValue = state.value;
            displayValue = newValue;
          }
        } else {
          parsedValue = newValue as T;
          displayValue = formatter.format(parsedValue);
        }
      } else {
        parsedValue = newValue as T;
        displayValue = String(newValue);
      }

      const validation = validate(parsedValue);
      
      setState((prev) => ({
        value: parsedValue,
        displayValue,
        isValid: validation.isValid,
        isDirty: true,
        isTouched: prev.isTouched,
        error: validation.error,
      }));

      const changeEvent: EntryChangeEvent<T> = {
        value: parsedValue,
        displayValue,
        isValid: validation.isValid,
      };

      onChange?.(parsedValue);
      onValidate?.(validation.isValid);

      return changeEvent;
    },
    [formatter, onChange, onValidate, state.value, validate]
  );

  const handleBlur = useCallback(() => {
    setState((prev) => {
      if (formatter && prev.isDirty) {
        try {
          const parsedValue = formatter.parse(prev.displayValue);
          const formattedValue = formatter.format(parsedValue);
          const validation = validate(parsedValue);

          return {
            ...prev,
            value: parsedValue,
            displayValue: formattedValue,
            isValid: validation.isValid,
            isTouched: true,
            error: validation.error,
          };
        } catch (error) {
          return {
            ...prev,
            isValid: false,
            isTouched: true,
            error: "Invalid format",
          };
        }
      }

      return {
        ...prev,
        isTouched: true,
      };
    });
  }, [formatter, validate]);

  const reset = useCallback(() => {
    const value = initialValue as T;
    const displayValue = formatter ? formatter.format(value) : String(value);
    setState({
      value,
      displayValue,
      isValid: true,
      isDirty: false,
      isTouched: false,
    });
  }, [formatter, initialValue]);

  useEffect(() => {
    if (initialValue !== undefined && initialValue !== state.value) {
      handleChange(initialValue);
    }
  }, [initialValue]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    value: state.value,
    displayValue: state.displayValue,
    isValid: state.isValid,
    isDirty: state.isDirty,
    isTouched: state.isTouched,
    error: state.error,
    handleChange,
    handleBlur,
    reset,
  };
}

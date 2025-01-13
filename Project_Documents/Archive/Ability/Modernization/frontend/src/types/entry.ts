import { z } from "zod";

export interface EntryValidation<T> {
  validate: (value: T) => boolean;
  message: string;
}

export interface EntryFormatter<T> {
  format: (value: T) => string;
  parse: (value: string) => T;
}

export interface EntryState<T> {
  value: T;
  displayValue: string;
  isValid: boolean;
  isDirty: boolean;
  isTouched: boolean;
  error?: string;
}

export interface EntryConfig<T> {
  initialValue?: T;
  placeholder?: string;
  label?: string;
  required?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  autoFocus?: boolean;
  className?: string;
  validation?: EntryValidation<T>[];
  formatter?: EntryFormatter<T>;
  schema?: z.ZodType<T>;
  onChange?: (value: T) => void;
  onValidate?: (isValid: boolean) => void;
}

export type EntryChangeEvent<T> = {
  value: T;
  displayValue: string;
  isValid: boolean;
};

export const createNumberFormatter = (
  locale: string = "en-US",
  options: Intl.NumberFormatOptions = {}
): EntryFormatter<number> => ({
  format: (value: number) =>
    new Intl.NumberFormat(locale, options).format(value),
  parse: (value: string) =>
    Number(value.replace(/[^-0-9.]/g, "")),
});

export const createDateFormatter = (
  locale: string = "en-US",
  options: Intl.DateTimeFormatOptions = {}
): EntryFormatter<Date> => ({
  format: (value: Date) =>
    new Intl.DateTimeFormat(locale, options).format(value),
  parse: (value: string) => new Date(value),
});

export const createCurrencyFormatter = (
  locale: string = "en-US",
  currency: string = "USD"
): EntryFormatter<number> => ({
  format: (value: number) =>
    new Intl.NumberFormat(locale, {
      style: "currency",
      currency,
    }).format(value),
  parse: (value: string) =>
    Number(value.replace(/[^-0-9.]/g, "")),
});

export const commonValidations = {
  required: <T>(message: string = "This field is required"): EntryValidation<T> => ({
    validate: (value: T) => value !== undefined && value !== null && value !== "",
    message,
  }),
  min: (min: number, message?: string): EntryValidation<number> => ({
    validate: (value: number) => value >= min,
    message: message || `Value must be at least ${min}`,
  }),
  max: (max: number, message?: string): EntryValidation<number> => ({
    validate: (value: number) => value <= max,
    message: message || `Value must be at most ${max}`,
  }),
  minLength: (min: number, message?: string): EntryValidation<string> => ({
    validate: (value: string) => value.length >= min,
    message: message || `Must be at least ${min} characters`,
  }),
  maxLength: (max: number, message?: string): EntryValidation<string> => ({
    validate: (value: string) => value.length <= max,
    message: message || `Must be at most ${max} characters`,
  }),
  pattern: (regex: RegExp, message: string): EntryValidation<string> => ({
    validate: (value: string) => regex.test(value),
    message,
  }),
  email: (message: string = "Invalid email address"): EntryValidation<string> => ({
    validate: (value: string) =>
      /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(value),
    message,
  }),
  phone: (message: string = "Invalid phone number"): EntryValidation<string> => ({
    validate: (value: string) =>
      /^\+?[\d\s-]{10,}$/.test(value.replace(/[\s-]/g, "")),
    message,
  }),
};

import { z } from 'zod'
import { useForm, UseFormReturn, FieldValues } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

export interface ValidationOptions<T> {
  /** The validation schema */
  schema: z.ZodType<T>
  /** Default form values */
  defaultValues?: Partial<T>
  /** Mode for running validation */
  mode?: 'onSubmit' | 'onChange' | 'onBlur' | 'onTouched'
  /** Callback when validation succeeds */
  onSuccess?: (data: T) => void
  /** Callback when validation fails */
  onError?: (errors: any) => void
}

export function useFormValidation<T extends FieldValues>({
  schema,
  defaultValues,
  mode = 'onSubmit',
  onSuccess,
  onError
}: ValidationOptions<T>): UseFormReturn<T> {
  const methods = useForm<T>({
    resolver: zodResolver(schema),
    defaultValues,
    mode
  })

  const { handleSubmit } = methods

  const onSubmit = handleSubmit(
    (data) => {
      onSuccess?.(data)
    },
    (errors) => {
      onError?.(errors)
    }
  )

  return {
    ...methods,
    handleSubmit: onSubmit
  }
}

// Validation schemas
export const createValidationSchema = <T extends Record<string, any>>(schema: T) => {
  return z.object(schema)
}

// Common validation rules
export const validationRules = {
  required: (message = 'This field is required') => z.string().min(1, message),
  email: (message = 'Invalid email address') =>
    z.string().email(message),
  min: (length: number, message = `Minimum ${length} characters required`) =>
    z.string().min(length, message),
  max: (length: number, message = `Maximum ${length} characters allowed`) =>
    z.string().max(length, message),
  pattern: (regex: RegExp, message = 'Invalid format') =>
    z.string().regex(regex, message),
  number: (message = 'Must be a number') =>
    z.number().or(z.string().regex(/^\d+$/).transform(Number)),
  integer: (message = 'Must be an integer') =>
    z.number().int(message),
  positive: (message = 'Must be a positive number') =>
    z.number().positive(message),
  url: (message = 'Invalid URL') =>
    z.string().url(message),
  date: (message = 'Invalid date') =>
    z.date({
      required_error: message,
      invalid_type_error: message
    }),
  boolean: () => z.boolean(),
  array: <T extends z.ZodType>(schema: T) => z.array(schema),
  object: <T extends z.ZodRawShape>(schema: T) => z.object(schema),
  enum: <T extends [string, ...string[]]>(values: T, message = 'Invalid option') =>
    z.enum(values, { errorMap: () => ({ message }) }),
  custom: <T>(
    validator: (value: T) => boolean,
    message = 'Invalid value'
  ) =>
    z.any().refine(validator, message)
}

// Example usage:
/*
const schema = createValidationSchema({
  username: validationRules.required()
    .pipe(validationRules.min(3))
    .pipe(validationRules.max(20)),
  email: validationRules.required()
    .pipe(validationRules.email()),
  age: validationRules.number()
    .pipe(validationRules.positive())
    .pipe(validationRules.integer()),
  website: validationRules.url(),
  terms: validationRules.boolean()
    .refine((val) => val === true, 'Terms must be accepted')
})
*/

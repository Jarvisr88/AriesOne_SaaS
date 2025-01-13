import React, { createContext, useContext, useCallback } from 'react'
import styled from 'styled-components'
import { useForm, UseFormReturn, FieldValues, Path } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

export interface FormProps<T extends FieldValues> {
  /** Form schema for validation */
  schema?: z.ZodType<T>
  /** Default values for form fields */
  defaultValues?: Partial<T>
  /** Called when form is submitted successfully */
  onSubmit: (values: T) => void | Promise<void>
  /** Called when form submission fails */
  onError?: (errors: any) => void
  /** Form children */
  children: React.ReactNode
  /** Additional CSS class */
  className?: string
  /** Form ID */
  id?: string
}

interface FormContextValue<T extends FieldValues> extends UseFormReturn<T> {
  schema?: z.ZodType<T>
}

const FormContext = createContext<FormContextValue<any> | null>(null)

export const useFormContext = <T extends FieldValues>() => {
  const context = useContext(FormContext)
  if (!context) {
    throw new Error('useFormContext must be used within a FormProvider')
  }
  return context as FormContextValue<T>
}

const StyledForm = styled.form`
  width: 100%;
`

export const FormContainer = styled.div<{ layout?: 'vertical' | 'horizontal' }>`
  display: flex;
  flex-direction: ${props => props.layout === 'horizontal' ? 'row' : 'column'};
  gap: ${props => props.theme.spacing.md};
`

export const FormGroup = styled.div<{
  layout?: 'vertical' | 'horizontal'
  columns?: number
}>`
  display: grid;
  grid-template-columns: ${props => props.columns ? `repeat(${props.columns}, 1fr)` : '1fr'};
  gap: ${props => props.theme.spacing.md};
  width: 100%;
`

export const FormSection = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.lg};
  border: 1px solid ${props => props.theme.colors.neutral[200]};
  border-radius: ${props => props.theme.radii.md};
`

export const FormDivider = styled.hr`
  border: none;
  border-top: 1px solid ${props => props.theme.colors.neutral[200]};
  margin: ${props => props.theme.spacing.md} 0;
`

export const FormLabel = styled.label<{ required?: boolean }>`
  display: block;
  margin-bottom: ${props => props.theme.spacing.xs};
  color: ${props => props.theme.colors.neutral[700]};
  font-size: ${props => props.theme.fontSizes.sm};
  font-weight: ${props => props.theme.fontWeights.medium};

  ${props => props.required && `
    &::after {
      content: '*';
      color: ${props.theme.colors.error[500]};
      margin-left: ${props.theme.spacing.xs};
    }
  `}
`

export const FormHelperText = styled.div<{ error?: boolean }>`
  margin-top: ${props => props.theme.spacing.xs};
  color: ${props => props.error ? props.theme.colors.error[500] : props.theme.colors.neutral[500]};
  font-size: ${props => props.theme.fontSizes.sm};
`

export const FormErrorMessage = styled.div`
  color: ${props => props.theme.colors.error[500]};
  font-size: ${props => props.theme.fontSizes.sm};
  margin-top: ${props => props.theme.spacing.xs};
`

export interface FormFieldProps<T extends FieldValues> {
  /** Field name */
  name: Path<T>
  /** Field label */
  label?: string
  /** Helper text */
  helperText?: string
  /** If true, the field is required */
  required?: boolean
  /** Children */
  children: React.ReactNode
  /** Additional CSS class */
  className?: string
}

export function FormField<T extends FieldValues>({
  name,
  label,
  helperText,
  required,
  children,
  className
}: FormFieldProps<T>) {
  const { formState: { errors } } = useFormContext<T>()
  const error = errors[name]

  return (
    <div className={className}>
      {label && (
        <FormLabel htmlFor={name} required={required}>
          {label}
        </FormLabel>
      )}
      {children}
      {helperText && !error && (
        <FormHelperText>{helperText}</FormHelperText>
      )}
      {error && (
        <FormErrorMessage>
          {error.message as string}
        </FormErrorMessage>
      )}
    </div>
  )
}

export function Form<T extends FieldValues>({
  schema,
  defaultValues,
  onSubmit,
  onError,
  children,
  className,
  id
}: FormProps<T>) {
  const methods = useForm<T>({
    resolver: schema ? zodResolver(schema) : undefined,
    defaultValues
  })

  const handleSubmit = useCallback(
    async (values: T) => {
      try {
        await onSubmit(values)
      } catch (error) {
        onError?.(error)
      }
    },
    [onSubmit, onError]
  )

  return (
    <FormContext.Provider value={{ ...methods, schema }}>
      <StyledForm
        id={id}
        className={className}
        onSubmit={methods.handleSubmit(handleSubmit)}
        noValidate
      >
        {children}
      </StyledForm>
    </FormContext.Provider>
  )
}

Form.displayName = 'Form'
FormField.displayName = 'FormField'

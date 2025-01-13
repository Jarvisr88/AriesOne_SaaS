import React from 'react'
import styled from 'styled-components'
import { FieldError, FieldErrors } from 'react-hook-form'

export interface ErrorMessageProps {
  /** The error object from react-hook-form */
  error?: FieldError
  /** Custom error message */
  message?: string
  /** Additional CSS class */
  className?: string
}

export interface ErrorSummaryProps {
  /** The errors object from react-hook-form */
  errors: FieldErrors
  /** The title of the error summary */
  title?: string
  /** Additional CSS class */
  className?: string
}

const ErrorContainer = styled.div`
  color: ${props => props.theme.colors.error[500]};
  font-size: ${props => props.theme.fontSizes.sm};
  margin-top: ${props => props.theme.spacing.xs};
`

const ErrorSummaryContainer = styled.div`
  border: 1px solid ${props => props.theme.colors.error[300]};
  border-radius: ${props => props.theme.radii.md};
  padding: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.error[50]};
`

const ErrorSummaryTitle = styled.h3`
  color: ${props => props.theme.colors.error[700]};
  margin: 0 0 ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.fontSizes.md};
  font-weight: ${props => props.theme.fontWeights.medium};
`

const ErrorList = styled.ul`
  margin: 0;
  padding-left: ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.error[700]};
`

const ErrorItem = styled.li`
  margin-bottom: ${props => props.theme.spacing.xs};

  &:last-child {
    margin-bottom: 0;
  }
`

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  error,
  message,
  className
}) => {
  if (!error && !message) return null

  return (
    <ErrorContainer
      role="alert"
      className={className}
    >
      {message || error?.message}
    </ErrorContainer>
  )
}

export const ErrorSummary: React.FC<ErrorSummaryProps> = ({
  errors,
  title = 'Please fix the following errors:',
  className
}) => {
  const errorList = Object.entries(errors)

  if (errorList.length === 0) return null

  return (
    <ErrorSummaryContainer
      role="alert"
      className={className}
    >
      <ErrorSummaryTitle>{title}</ErrorSummaryTitle>
      <ErrorList>
        {errorList.map(([field, error]) => (
          <ErrorItem key={field}>
            {error.message}
          </ErrorItem>
        ))}
      </ErrorList>
    </ErrorSummaryContainer>
  )
}

// Error boundary component for handling form-level errors
export class FormErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Form Error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <ErrorSummaryContainer role="alert">
            <ErrorSummaryTitle>
              Something went wrong with the form.
            </ErrorSummaryTitle>
            <p>Please try again or contact support if the problem persists.</p>
          </ErrorSummaryContainer>
        )
      )
    }

    return this.props.children
  }
}

// Helper function to format error messages
export const formatError = (error: any): string => {
  if (typeof error === 'string') return error
  if (error?.message) return error.message
  if (Array.isArray(error)) return error[0]
  return 'An error occurred'
}

// Helper function to check if a field has an error
export const hasError = (errors: FieldErrors, name: string): boolean => {
  return Boolean(errors[name])
}

ErrorMessage.displayName = 'ErrorMessage'
ErrorSummary.displayName = 'ErrorSummary'
FormErrorBoundary.displayName = 'FormErrorBoundary'

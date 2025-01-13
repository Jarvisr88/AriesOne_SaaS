import React from 'react'
import styled from 'styled-components'
import { useFormContext } from 'react-hook-form'
import { ErrorMessage } from './ErrorHandling'

export interface FieldGroupProps {
  /** The title of the field group */
  title?: string
  /** Description text */
  description?: string
  /** Children elements */
  children: React.ReactNode
  /** Additional CSS class */
  className?: string
}

export interface FieldProps {
  /** The name of the field */
  name: string
  /** The label for the field */
  label?: string
  /** Helper text */
  helperText?: string
  /** If true, the field is required */
  required?: boolean
  /** If true, the field is disabled */
  disabled?: boolean
  /** Children elements */
  children: React.ReactNode
  /** Additional CSS class */
  className?: string
}

const GroupContainer = styled.fieldset`
  border: 1px solid ${props => props.theme.colors.neutral[200]};
  border-radius: ${props => props.theme.radii.md};
  padding: ${props => props.theme.spacing.lg};
  margin: 0 0 ${props => props.theme.spacing.md};

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`

const GroupTitle = styled.legend`
  font-size: ${props => props.theme.fontSizes.md};
  font-weight: ${props => props.theme.fontWeights.medium};
  color: ${props => props.theme.colors.neutral[900]};
  padding: 0 ${props => props.theme.spacing.sm};
`

const GroupDescription = styled.div`
  font-size: ${props => props.theme.fontSizes.sm};
  color: ${props => props.theme.colors.neutral[600]};
  margin-bottom: ${props => props.theme.spacing.md};
`

const FieldContainer = styled.div`
  margin-bottom: ${props => props.theme.spacing.md};

  &:last-child {
    margin-bottom: 0;
  }
`

const FieldLabel = styled.label<{ required?: boolean }>`
  display: block;
  margin-bottom: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.fontSizes.sm};
  font-weight: ${props => props.theme.fontWeights.medium};
  color: ${props => props.theme.colors.neutral[700]};

  ${props =>
    props.required &&
    `
    &::after {
      content: '*';
      color: ${props.theme.colors.error[500]};
      margin-left: ${props.theme.spacing.xs};
    }
  `}
`

const HelperText = styled.div`
  font-size: ${props => props.theme.fontSizes.sm};
  color: ${props => props.theme.colors.neutral[600]};
  margin-top: ${props => props.theme.spacing.xs};
`

export const FieldGroup: React.FC<FieldGroupProps> = ({
  title,
  description,
  children,
  className
}) => {
  return (
    <GroupContainer className={className}>
      {title && <GroupTitle>{title}</GroupTitle>}
      {description && <GroupDescription>{description}</GroupDescription>}
      {children}
    </GroupContainer>
  )
}

export const Field: React.FC<FieldProps> = ({
  name,
  label,
  helperText,
  required,
  disabled,
  children,
  className
}) => {
  const { formState: { errors } } = useFormContext()
  const error = errors[name]

  return (
    <FieldContainer className={className}>
      {label && (
        <FieldLabel
          htmlFor={name}
          required={required}
        >
          {label}
        </FieldLabel>
      )}
      {React.cloneElement(React.Children.only(children), {
        id: name,
        'aria-describedby': helperText ? `${name}-helper` : undefined,
        disabled
      })}
      {helperText && !error && (
        <HelperText id={`${name}-helper`}>
          {helperText}
        </HelperText>
      )}
      <ErrorMessage error={error} />
    </FieldContainer>
  )
}

// Inline field group for horizontal layout
const InlineGroupContainer = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.md};

  @media (max-width: ${props => props.theme.breakpoints.sm}) {
    flex-direction: column;
    align-items: stretch;
  }
`

export interface InlineFieldGroupProps {
  /** Children elements */
  children: React.ReactNode
  /** Additional CSS class */
  className?: string
}

export const InlineFieldGroup: React.FC<InlineFieldGroupProps> = ({
  children,
  className
}) => {
  return (
    <InlineGroupContainer className={className}>
      {children}
    </InlineGroupContainer>
  )
}

// Repeatable field group for dynamic form fields
const RepeatableGroupContainer = styled.div`
  margin-bottom: ${props => props.theme.spacing.md};
`

const RepeatableGroupActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${props => props.theme.spacing.sm};
  margin-top: ${props => props.theme.spacing.sm};
`

export interface RepeatableFieldGroupProps {
  /** Children elements */
  children: React.ReactNode
  /** Called when add button is clicked */
  onAdd: () => void
  /** Called when remove button is clicked */
  onRemove: () => void
  /** If true, the remove button is disabled */
  canRemove?: boolean
  /** Additional CSS class */
  className?: string
}

export const RepeatableFieldGroup: React.FC<RepeatableFieldGroupProps> = ({
  children,
  onAdd,
  onRemove,
  canRemove = true,
  className
}) => {
  return (
    <RepeatableGroupContainer className={className}>
      {children}
      <RepeatableGroupActions>
        <button
          type="button"
          onClick={onAdd}
        >
          Add
        </button>
        {canRemove && (
          <button
            type="button"
            onClick={onRemove}
          >
            Remove
          </button>
        )}
      </RepeatableGroupActions>
    </RepeatableGroupContainer>
  )
}

FieldGroup.displayName = 'FieldGroup'
Field.displayName = 'Field'
InlineFieldGroup.displayName = 'InlineFieldGroup'
RepeatableFieldGroup.displayName = 'RepeatableFieldGroup'

import React, { forwardRef, useState, useCallback } from 'react'
import styled, { css } from 'styled-components'
import { Theme } from '../../theme/theme'

export type InputSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
export type InputVariant = 'outline' | 'filled' | 'flushed' | 'unstyled'

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** The size of the input */
  size?: InputSize
  /** The variant of the input */
  variant?: InputVariant
  /** If true, the input will be disabled */
  isDisabled?: boolean
  /** If true, the input will be read only */
  isReadOnly?: boolean
  /** If true, the input will be required */
  isRequired?: boolean
  /** If true, the input will be invalid */
  isInvalid?: boolean
  /** The label for the input */
  label?: string
  /** The helper text to show below the input */
  helperText?: string
  /** The error message to show when input is invalid */
  errorMessage?: string
  /** The left icon */
  leftIcon?: React.ReactElement
  /** The right icon */
  rightIcon?: React.ReactElement
  /** The left addon */
  leftAddon?: React.ReactNode
  /** The right addon */
  rightAddon?: React.ReactNode
  /** If true, the input will take up the full width of its container */
  isFullWidth?: boolean
}

const sizeStyles = {
  xs: css`
    height: 1.5rem;
    font-size: ${props => props.theme.fontSizes.xs};
    padding-left: ${props => props.theme.spacing.xs};
    padding-right: ${props => props.theme.spacing.xs};
  `,
  sm: css`
    height: 2rem;
    font-size: ${props => props.theme.fontSizes.sm};
    padding-left: ${props => props.theme.spacing.sm};
    padding-right: ${props => props.theme.spacing.sm};
  `,
  md: css`
    height: 2.5rem;
    font-size: ${props => props.theme.fontSizes.md};
    padding-left: ${props => props.theme.spacing.md};
    padding-right: ${props => props.theme.spacing.md};
  `,
  lg: css`
    height: 3rem;
    font-size: ${props => props.theme.fontSizes.lg};
    padding-left: ${props => props.theme.spacing.lg};
    padding-right: ${props => props.theme.spacing.lg};
  `,
  xl: css`
    height: 3.5rem;
    font-size: ${props => props.theme.fontSizes.xl};
    padding-left: ${props => props.theme.spacing.xl};
    padding-right: ${props => props.theme.spacing.xl};
  `
}

const variantStyles = {
  outline: css`
    border: 1px solid ${props => props.theme.colors.neutral[200]};
    background-color: ${props => props.theme.colors.white};

    &:hover:not(:disabled):not(:read-only) {
      border-color: ${props => props.theme.colors.neutral[300]};
    }

    &:focus-visible:not(:disabled):not(:read-only) {
      border-color: ${props => props.theme.colors.primary[500]};
      box-shadow: 0 0 0 1px ${props => props.theme.colors.primary[500]};
    }
  `,
  filled: css`
    border: 2px solid transparent;
    background-color: ${props => props.theme.colors.neutral[100]};

    &:hover:not(:disabled):not(:read-only) {
      background-color: ${props => props.theme.colors.neutral[200]};
    }

    &:focus-visible:not(:disabled):not(:read-only) {
      background-color: ${props => props.theme.colors.white};
      border-color: ${props => props.theme.colors.primary[500]};
    }
  `,
  flushed: css`
    border: none;
    border-bottom: 1px solid ${props => props.theme.colors.neutral[200]};
    border-radius: 0;
    padding-left: 0;
    padding-right: 0;

    &:hover:not(:disabled):not(:read-only) {
      border-bottom-color: ${props => props.theme.colors.neutral[300]};
    }

    &:focus-visible:not(:disabled):not(:read-only) {
      border-bottom-color: ${props => props.theme.colors.primary[500]};
      box-shadow: 0 1px 0 0 ${props => props.theme.colors.primary[500]};
    }
  `,
  unstyled: css`
    border: none;
    padding: 0;
    height: auto;
    background: none;
  `
}

const InputWrapper = styled.div<{ isFullWidth?: boolean }>`
  display: inline-flex;
  flex-direction: column;
  position: relative;
  width: ${props => props.isFullWidth ? '100%' : 'auto'};
`

const Label = styled.label<{ size?: InputSize }>`
  margin-bottom: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.fontSizes[props.size === 'xs' || props.size === 'sm' ? 'xs' : 'sm']};
  font-weight: ${props => props.theme.fontWeights.medium};
  color: ${props => props.theme.colors.neutral[700]};
`

const InputGroup = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`

const StyledInput = styled.input<InputProps>`
  /* Base styles */
  width: 100%;
  border-radius: ${props => props.theme.radii.md};
  transition: ${props => props.theme.transitions.default};
  outline: none;
  appearance: none;

  /* Size styles */
  ${props => sizeStyles[props.size || 'md']}

  /* Variant styles */
  ${props => variantStyles[props.variant || 'outline']}

  /* Invalid styles */
  ${props =>
    props.isInvalid &&
    css`
      border-color: ${props.theme.colors.error[500]} !important;
      
      &:focus-visible {
        box-shadow: 0 0 0 1px ${props.theme.colors.error[500]} !important;
      }
    `}

  /* Disabled styles */
  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  /* Read only styles */
  &:read-only {
    background-color: ${props => props.theme.colors.neutral[50]};
    cursor: default;
  }

  /* Icon padding */
  ${props =>
    props.leftIcon &&
    css`
      padding-left: ${props.theme.spacing.xl};
    `}

  ${props =>
    props.rightIcon &&
    css`
      padding-right: ${props.theme.spacing.xl};
    `}

  /* Addon styles */
  ${props =>
    props.leftAddon &&
    css`
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    `}

  ${props =>
    props.rightAddon &&
    css`
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    `}
`

const IconWrapper = styled.div<{ position: 'left' | 'right' }>`
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  ${props => props.position}: ${props => props.theme.spacing.sm};
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  color: ${props => props.theme.colors.neutral[500]};
`

const Addon = styled.div<{ position: 'left' | 'right' }>`
  display: flex;
  align-items: center;
  padding: 0 ${props => props.theme.spacing.sm};
  background-color: ${props => props.theme.colors.neutral[100]};
  border: 1px solid ${props => props.theme.colors.neutral[200]};
  color: ${props => props.theme.colors.neutral[500]};
  
  ${props =>
    props.position === 'left'
      ? css`
          border-right: none;
          border-radius: ${props.theme.radii.md} 0 0 ${props.theme.radii.md};
        `
      : css`
          border-left: none;
          border-radius: 0 ${props.theme.radii.md} ${props.theme.radii.md} 0;
        `}
`

const HelperText = styled.div<{ isError?: boolean }>`
  margin-top: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.fontSizes.sm};
  color: ${props =>
    props.isError
      ? props.theme.colors.error[500]
      : props.theme.colors.neutral[500]};
`

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      size = 'md',
      variant = 'outline',
      isDisabled = false,
      isReadOnly = false,
      isRequired = false,
      isInvalid = false,
      label,
      helperText,
      errorMessage,
      leftIcon,
      rightIcon,
      leftAddon,
      rightAddon,
      isFullWidth = false,
      id,
      'aria-describedby': ariaDescribedBy,
      ...props
    },
    ref
  ) => {
    const [uniqueId] = useState(() => id || `input-${Math.random().toString(36).substr(2, 9)}`)
    const helperId = `${uniqueId}-helper`
    const errorId = `${uniqueId}-error`

    const getAriaDescribedBy = useCallback(() => {
      const ids = []
      if (ariaDescribedBy) ids.push(ariaDescribedBy)
      if (helperText && !isInvalid) ids.push(helperId)
      if (errorMessage && isInvalid) ids.push(errorId)
      return ids.join(' ')
    }, [ariaDescribedBy, helperText, errorMessage, isInvalid, helperId, errorId])

    return (
      <InputWrapper isFullWidth={isFullWidth}>
        {label && (
          <Label
            htmlFor={uniqueId}
            size={size}
          >
            {label}
            {isRequired && (
              <span
                aria-hidden="true"
                style={{ color: 'red', marginLeft: '0.25rem' }}
              >
                *
              </span>
            )}
          </Label>
        )}

        <InputGroup>
          {leftAddon && <Addon position="left">{leftAddon}</Addon>}
          {leftIcon && <IconWrapper position="left">{leftIcon}</IconWrapper>}

          <StyledInput
            ref={ref}
            id={uniqueId}
            size={size}
            variant={variant}
            disabled={isDisabled}
            readOnly={isReadOnly}
            required={isRequired}
            aria-invalid={isInvalid}
            aria-describedby={getAriaDescribedBy()}
            leftIcon={leftIcon}
            rightIcon={rightIcon}
            leftAddon={leftAddon}
            rightAddon={rightAddon}
            {...props}
          />

          {rightIcon && <IconWrapper position="right">{rightIcon}</IconWrapper>}
          {rightAddon && <Addon position="right">{rightAddon}</Addon>}
        </InputGroup>

        {(helperText || errorMessage) && (
          <HelperText
            id={isInvalid ? errorId : helperId}
            isError={isInvalid}
          >
            {isInvalid ? errorMessage : helperText}
          </HelperText>
        )}
      </InputWrapper>
    )
  }
)

Input.displayName = 'Input'

import React, { forwardRef, useState, useCallback, useEffect, useRef } from 'react'
import styled, { css } from 'styled-components'
import { Theme } from '../../theme/theme'

export type SelectSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
export type SelectVariant = 'outline' | 'filled' | 'flushed' | 'unstyled'

export interface SelectOption {
  value: string
  label: string
  isDisabled?: boolean
}

export interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'size' | 'multiple'> {
  /** The size of the select */
  size?: SelectSize
  /** The variant of the select */
  variant?: SelectVariant
  /** If true, the select will be disabled */
  isDisabled?: boolean
  /** If true, the select will be required */
  isRequired?: boolean
  /** If true, the select will be invalid */
  isInvalid?: boolean
  /** If true, multiple options can be selected */
  isMulti?: boolean
  /** The label for the select */
  label?: string
  /** The helper text to show below the select */
  helperText?: string
  /** The error message to show when select is invalid */
  errorMessage?: string
  /** The placeholder text */
  placeholder?: string
  /** The options for the select */
  options: SelectOption[]
  /** If true, the select will take up the full width of its container */
  isFullWidth?: boolean
  /** Called when selected value changes */
  onChange?: (value: string | string[]) => void
}

const sizeStyles = {
  xs: css`
    height: 1.5rem;
    font-size: ${props => props.theme.fontSizes.xs};
    padding: 0 ${props => props.theme.spacing.xs};
  `,
  sm: css`
    height: 2rem;
    font-size: ${props => props.theme.fontSizes.sm};
    padding: 0 ${props => props.theme.spacing.sm};
  `,
  md: css`
    height: 2.5rem;
    font-size: ${props => props.theme.fontSizes.md};
    padding: 0 ${props => props.theme.spacing.md};
  `,
  lg: css`
    height: 3rem;
    font-size: ${props => props.theme.fontSizes.lg};
    padding: 0 ${props => props.theme.spacing.lg};
  `,
  xl: css`
    height: 3.5rem;
    font-size: ${props => props.theme.fontSizes.xl};
    padding: 0 ${props => props.theme.spacing.xl};
  `
}

const variantStyles = {
  outline: css`
    border: 1px solid ${props => props.theme.colors.neutral[200]};
    background-color: ${props => props.theme.colors.white};

    &:hover:not(:disabled) {
      border-color: ${props => props.theme.colors.neutral[300]};
    }

    &:focus-visible:not(:disabled) {
      border-color: ${props => props.theme.colors.primary[500]};
      box-shadow: 0 0 0 1px ${props => props.theme.colors.primary[500]};
    }
  `,
  filled: css`
    border: 2px solid transparent;
    background-color: ${props => props.theme.colors.neutral[100]};

    &:hover:not(:disabled) {
      background-color: ${props => props.theme.colors.neutral[200]};
    }

    &:focus-visible:not(:disabled) {
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

    &:hover:not(:disabled) {
      border-bottom-color: ${props => props.theme.colors.neutral[300]};
    }

    &:focus-visible:not(:disabled) {
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

const SelectWrapper = styled.div<{ isFullWidth?: boolean }>`
  display: inline-flex;
  flex-direction: column;
  position: relative;
  width: ${props => props.isFullWidth ? '100%' : 'auto'};
`

const Label = styled.label<{ size?: SelectSize }>`
  margin-bottom: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.fontSizes[props.size === 'xs' || props.size === 'sm' ? 'xs' : 'sm']};
  font-weight: ${props => props.theme.fontWeights.medium};
  color: ${props => props.theme.colors.neutral[700]};
`

const SelectContainer = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`

const StyledSelect = styled.select<SelectProps>`
  /* Base styles */
  width: 100%;
  border-radius: ${props => props.theme.radii.md};
  transition: ${props => props.theme.transitions.default};
  outline: none;
  appearance: none;
  cursor: pointer;

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

  /* Placeholder styles */
  &:invalid {
    color: ${props => props.theme.colors.neutral[400]};
  }

  /* Remove default arrow in IE */
  &::-ms-expand {
    display: none;
  }

  /* Option styles */
  option {
    color: ${props => props.theme.colors.neutral[900]};
    background-color: ${props => props.theme.colors.white};
    
    &:disabled {
      color: ${props => props.theme.colors.neutral[400]};
    }
  }

  /* Multiple select styles */
  ${props =>
    props.isMulti &&
    css`
      height: auto;
      min-height: ${sizeStyles[props.size || 'md']};
      padding: ${props.theme.spacing.xs};
      
      option {
        padding: ${props.theme.spacing.xs};
      }
    `}
`

const CaretIcon = styled.div<{ isOpen?: boolean }>`
  position: absolute;
  right: ${props => props.theme.spacing.sm};
  top: 50%;
  transform: translateY(-50%) ${props => props.isOpen ? 'rotate(180deg)' : 'rotate(0)'};
  pointer-events: none;
  transition: transform 0.2s;
  
  &::before {
    content: '';
    display: block;
    width: 0.5em;
    height: 0.5em;
    border-right: 2px solid ${props => props.theme.colors.neutral[400]};
    border-bottom: 2px solid ${props => props.theme.colors.neutral[400]};
    transform: rotate(45deg);
  }
`

const HelperText = styled.div<{ isError?: boolean }>`
  margin-top: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.fontSizes.sm};
  color: ${props =>
    props.isError
      ? props.theme.colors.error[500]
      : props.theme.colors.neutral[500]};
`

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      size = 'md',
      variant = 'outline',
      isDisabled = false,
      isRequired = false,
      isInvalid = false,
      isMulti = false,
      label,
      helperText,
      errorMessage,
      placeholder,
      options,
      isFullWidth = false,
      onChange,
      id,
      'aria-describedby': ariaDescribedBy,
      ...props
    },
    ref
  ) => {
    const [uniqueId] = useState(() => id || `select-${Math.random().toString(36).substr(2, 9)}`)
    const [isOpen, setIsOpen] = useState(false)
    const helperId = `${uniqueId}-helper`
    const errorId = `${uniqueId}-error`
    const selectRef = useRef<HTMLSelectElement>(null)

    const handleChange = useCallback(
      (event: React.ChangeEvent<HTMLSelectElement>) => {
        if (onChange) {
          if (isMulti) {
            const selectedOptions = Array.from(event.target.selectedOptions)
            onChange(selectedOptions.map(option => option.value))
          } else {
            onChange(event.target.value)
          }
        }
      },
      [onChange, isMulti]
    )

    const getAriaDescribedBy = useCallback(() => {
      const ids = []
      if (ariaDescribedBy) ids.push(ariaDescribedBy)
      if (helperText && !isInvalid) ids.push(helperId)
      if (errorMessage && isInvalid) ids.push(errorId)
      return ids.join(' ')
    }, [ariaDescribedBy, helperText, errorMessage, isInvalid, helperId, errorId])

    useEffect(() => {
      const handleFocus = () => setIsOpen(true)
      const handleBlur = () => setIsOpen(false)

      const select = selectRef.current
      if (select) {
        select.addEventListener('focus', handleFocus)
        select.addEventListener('blur', handleBlur)
      }

      return () => {
        if (select) {
          select.removeEventListener('focus', handleFocus)
          select.removeEventListener('blur', handleBlur)
        }
      }
    }, [])

    return (
      <SelectWrapper isFullWidth={isFullWidth}>
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

        <SelectContainer>
          <StyledSelect
            ref={el => {
              if (typeof ref === 'function') {
                ref(el)
              } else if (ref) {
                ref.current = el
              }
              selectRef.current = el
            }}
            id={uniqueId}
            size={size}
            variant={variant}
            disabled={isDisabled}
            required={isRequired}
            aria-invalid={isInvalid}
            aria-describedby={getAriaDescribedBy()}
            multiple={isMulti}
            onChange={handleChange}
            {...props}
          >
            {placeholder && !isMulti && (
              <option value="" disabled hidden>
                {placeholder}
              </option>
            )}
            {options.map(option => (
              <option
                key={option.value}
                value={option.value}
                disabled={option.isDisabled}
              >
                {option.label}
              </option>
            ))}
          </StyledSelect>

          {!isMulti && <CaretIcon isOpen={isOpen} />}
        </SelectContainer>

        {(helperText || errorMessage) && (
          <HelperText
            id={isInvalid ? errorId : helperId}
            isError={isInvalid}
          >
            {isInvalid ? errorMessage : helperText}
          </HelperText>
        )}
      </SelectWrapper>
    )
  }
)

Select.displayName = 'Select'

import React, { forwardRef, useRef, useEffect } from 'react'
import styled, { css } from 'styled-components'
import { Theme } from '../../theme/theme'

export type CheckboxSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
export type CheckboxColorScheme = 'primary' | 'success' | 'warning' | 'error' | 'neutral'

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** The size of the checkbox */
  size?: CheckboxSize
  /** The color scheme of the checkbox */
  colorScheme?: CheckboxColorScheme
  /** If true, the checkbox will be disabled */
  isDisabled?: boolean
  /** If true, the checkbox will be read only */
  isReadOnly?: boolean
  /** If true, the checkbox will be invalid */
  isInvalid?: boolean
  /** If true, the checkbox will be in an indeterminate state */
  isIndeterminate?: boolean
  /** The label for the checkbox */
  label?: string
  /** The helper text to show below the checkbox */
  helperText?: string
  /** The error message to show when checkbox is invalid */
  errorMessage?: string
}

const sizeStyles = {
  xs: {
    box: '1rem',
    icon: '0.75rem',
    fontSize: 'xs'
  },
  sm: {
    box: '1.25rem',
    icon: '1rem',
    fontSize: 'sm'
  },
  md: {
    box: '1.5rem',
    icon: '1.25rem',
    fontSize: 'md'
  },
  lg: {
    box: '1.75rem',
    icon: '1.5rem',
    fontSize: 'lg'
  },
  xl: {
    box: '2rem',
    icon: '1.75rem',
    fontSize: 'xl'
  }
}

const CheckboxContainer = styled.label<{ isDisabled?: boolean }>`
  display: inline-flex;
  align-items: flex-start;
  position: relative;
  cursor: ${props => props.isDisabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.isDisabled ? 0.4 : 1};
`

const HiddenCheckbox = styled.input.attrs({ type: 'checkbox' })`
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
`

const StyledCheckbox = styled.div<{
  size?: CheckboxSize
  colorScheme?: CheckboxColorScheme
  isChecked?: boolean
  isIndeterminate?: boolean
  isInvalid?: boolean
  isDisabled?: boolean
  isReadOnly?: boolean
}>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: ${props => sizeStyles[props.size || 'md'].box};
  height: ${props => sizeStyles[props.size || 'md'].box};
  margin-right: ${props => props.theme.spacing.sm};
  border: 2px solid ${props => props.isInvalid
    ? props.theme.colors.error[500]
    : props.theme.colors[props.colorScheme || 'primary'][500]};
  border-radius: ${props => props.theme.radii.sm};
  background-color: ${props => props.isChecked || props.isIndeterminate
    ? props.theme.colors[props.colorScheme || 'primary'][500]
    : props.theme.colors.white};
  transition: ${props => props.theme.transitions.default};

  ${props => !props.isDisabled && !props.isReadOnly && css`
    &:hover {
      border-color: ${props.isInvalid
        ? props.theme.colors.error[600]
        : props.theme.colors[props.colorScheme || 'primary'][600]};
      background-color: ${props.isChecked || props.isIndeterminate
        ? props.theme.colors[props.colorScheme || 'primary'][600]
        : props.theme.colors.neutral[50]};
    }
  `}

  ${HiddenCheckbox}:focus-visible + & {
    box-shadow: 0 0 0 3px ${props => props.isInvalid
      ? props.theme.colors.error[200]
      : props.theme.colors[props.colorScheme || 'primary'][200]};
  }
`

const CheckIcon = styled.div<{ size?: CheckboxSize }>`
  width: ${props => sizeStyles[props.size || 'md'].icon};
  height: ${props => sizeStyles[props.size || 'md'].icon};
  color: ${props => props.theme.colors.white};
  
  &::before {
    content: '';
    display: block;
    width: 100%;
    height: 100%;
    background-position: center;
    background-repeat: no-repeat;
    background-size: contain;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E");
  }
`

const IndeterminateIcon = styled.div<{ size?: CheckboxSize }>`
  width: ${props => sizeStyles[props.size || 'md'].icon};
  height: ${props => sizeStyles[props.size || 'md'].icon};
  color: ${props => props.theme.colors.white};
  
  &::before {
    content: '';
    display: block;
    width: 100%;
    height: 100%;
    background-position: center;
    background-repeat: no-repeat;
    background-size: contain;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='5' y1='12' x2='19' y2='12'%3E%3C/line%3E%3C/svg%3E");
  }
`

const LabelText = styled.span<{ size?: CheckboxSize }>`
  font-size: ${props => props.theme.fontSizes[sizeStyles[props.size || 'md'].fontSize]};
  line-height: ${props => sizeStyles[props.size || 'md'].box};
`

const HelperText = styled.div<{ isError?: boolean; size?: CheckboxSize }>`
  margin-top: ${props => props.theme.spacing.xs};
  margin-left: calc(${props => sizeStyles[props.size || 'md'].box} + ${props => props.theme.spacing.sm});
  font-size: ${props => props.theme.fontSizes.sm};
  color: ${props =>
    props.isError
      ? props.theme.colors.error[500]
      : props.theme.colors.neutral[500]};
`

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  (
    {
      size = 'md',
      colorScheme = 'primary',
      isDisabled = false,
      isReadOnly = false,
      isInvalid = false,
      isIndeterminate = false,
      label,
      helperText,
      errorMessage,
      checked,
      defaultChecked,
      onChange,
      id,
      'aria-describedby': ariaDescribedBy,
      ...props
    },
    ref
  ) => {
    const inputRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
      if (inputRef.current) {
        inputRef.current.indeterminate = isIndeterminate
      }
    }, [isIndeterminate])

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      if (!isDisabled && !isReadOnly && onChange) {
        onChange(event)
      }
    }

    const [uniqueId] = useState(() => id || `checkbox-${Math.random().toString(36).substr(2, 9)}`)
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
      <div>
        <CheckboxContainer isDisabled={isDisabled}>
          <HiddenCheckbox
            ref={el => {
              if (typeof ref === 'function') {
                ref(el)
              } else if (ref) {
                ref.current = el
              }
              inputRef.current = el
            }}
            id={uniqueId}
            checked={checked}
            defaultChecked={defaultChecked}
            disabled={isDisabled}
            readOnly={isReadOnly}
            aria-invalid={isInvalid}
            aria-describedby={getAriaDescribedBy()}
            onChange={handleChange}
            {...props}
          />
          <StyledCheckbox
            size={size}
            colorScheme={colorScheme}
            isChecked={checked || defaultChecked}
            isIndeterminate={isIndeterminate}
            isInvalid={isInvalid}
            isDisabled={isDisabled}
            isReadOnly={isReadOnly}
          >
            {isIndeterminate ? (
              <IndeterminateIcon size={size} />
            ) : (
              checked && <CheckIcon size={size} />
            )}
          </StyledCheckbox>
          {label && <LabelText size={size}>{label}</LabelText>}
        </CheckboxContainer>

        {(helperText || errorMessage) && (
          <HelperText
            id={isInvalid ? errorId : helperId}
            isError={isInvalid}
            size={size}
          >
            {isInvalid ? errorMessage : helperText}
          </HelperText>
        )}
      </div>
    )
  }
)

Checkbox.displayName = 'Checkbox'

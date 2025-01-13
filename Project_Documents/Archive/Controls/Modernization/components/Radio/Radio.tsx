import React, { forwardRef, useContext, createContext, useCallback } from 'react'
import styled, { css } from 'styled-components'
import { Theme } from '../../theme/theme'

export type RadioSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
export type RadioColorScheme = 'primary' | 'success' | 'warning' | 'error' | 'neutral'

interface RadioContextValue {
  name?: string
  size?: RadioSize
  colorScheme?: RadioColorScheme
  value?: string
  onChange?: (value: string) => void
  isDisabled?: boolean
  isRequired?: boolean
  isInvalid?: boolean
}

const RadioContext = createContext<RadioContextValue>({})

export interface RadioGroupProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange'> {
  /** The name used for all radio buttons in the group */
  name: string
  /** The size of all radio buttons in the group */
  size?: RadioSize
  /** The color scheme of all radio buttons in the group */
  colorScheme?: RadioColorScheme
  /** The currently selected value */
  value?: string
  /** Called when selection changes */
  onChange?: (value: string) => void
  /** If true, all radio buttons in the group will be disabled */
  isDisabled?: boolean
  /** If true, one radio button in the group must be selected */
  isRequired?: boolean
  /** If true, all radio buttons in the group will be invalid */
  isInvalid?: boolean
  /** The helper text to show below the radio group */
  helperText?: string
  /** The error message to show when the group is invalid */
  errorMessage?: string
  /** The label for the radio group */
  label?: string
  /** The direction of the radio buttons (horizontal or vertical) */
  direction?: 'horizontal' | 'vertical'
}

export interface RadioProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** The size of the radio button */
  size?: RadioSize
  /** The color scheme of the radio button */
  colorScheme?: RadioColorScheme
  /** If true, the radio button will be disabled */
  isDisabled?: boolean
  /** If true, the radio button will be invalid */
  isInvalid?: boolean
  /** The label for the radio button */
  label?: string
}

const sizeStyles = {
  xs: {
    circle: '1rem',
    dot: '0.375rem',
    fontSize: 'xs'
  },
  sm: {
    circle: '1.25rem',
    dot: '0.5rem',
    fontSize: 'sm'
  },
  md: {
    circle: '1.5rem',
    dot: '0.625rem',
    fontSize: 'md'
  },
  lg: {
    circle: '1.75rem',
    dot: '0.75rem',
    fontSize: 'lg'
  },
  xl: {
    circle: '2rem',
    dot: '0.875rem',
    fontSize: 'xl'
  }
}

const RadioGroupContainer = styled.div<{ direction?: 'horizontal' | 'vertical' }>`
  display: flex;
  flex-direction: ${props => props.direction === 'horizontal' ? 'row' : 'column'};
  gap: ${props => props.theme.spacing.md};
`

const GroupLabel = styled.div<{ size?: RadioSize }>`
  margin-bottom: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.fontSizes[sizeStyles[props.size || 'md'].fontSize]};
  font-weight: ${props => props.theme.fontWeights.medium};
  color: ${props => props.theme.colors.neutral[700]};
`

const RadioContainer = styled.label<{ isDisabled?: boolean }>`
  display: inline-flex;
  align-items: center;
  position: relative;
  cursor: ${props => props.isDisabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.isDisabled ? 0.4 : 1};
`

const HiddenRadio = styled.input.attrs({ type: 'radio' })`
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
`

const StyledRadio = styled.div<{
  size?: RadioSize
  colorScheme?: RadioColorScheme
  isChecked?: boolean
  isInvalid?: boolean
  isDisabled?: boolean
}>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: ${props => sizeStyles[props.size || 'md'].circle};
  height: ${props => sizeStyles[props.size || 'md'].circle};
  margin-right: ${props => props.theme.spacing.sm};
  border: 2px solid ${props => props.isInvalid
    ? props.theme.colors.error[500]
    : props.isChecked
      ? props.theme.colors[props.colorScheme || 'primary'][500]
      : props.theme.colors.neutral[300]};
  border-radius: 50%;
  background-color: ${props => props.theme.colors.white};
  transition: ${props => props.theme.transitions.default};

  ${props => !props.isDisabled && css`
    &:hover {
      border-color: ${props.isInvalid
        ? props.theme.colors.error[600]
        : props.theme.colors[props.colorScheme || 'primary'][600]};
    }
  `}

  ${HiddenRadio}:focus-visible + & {
    box-shadow: 0 0 0 3px ${props => props.isInvalid
      ? props.theme.colors.error[200]
      : props.theme.colors[props.colorScheme || 'primary'][200]};
  }
`

const RadioDot = styled.div<{
  size?: RadioSize
  colorScheme?: RadioColorScheme
}>`
  width: ${props => sizeStyles[props.size || 'md'].dot};
  height: ${props => sizeStyles[props.size || 'md'].dot};
  border-radius: 50%;
  background-color: ${props =>
    props.theme.colors[props.colorScheme || 'primary'][500]};
  transform: scale(0);
  transition: transform 0.2s;

  ${HiddenRadio}:checked + ${StyledRadio} & {
    transform: scale(1);
  }
`

const LabelText = styled.span<{ size?: RadioSize }>`
  font-size: ${props => props.theme.fontSizes[sizeStyles[props.size || 'md'].fontSize]};
`

const HelperText = styled.div<{ isError?: boolean }>`
  margin-top: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.fontSizes.sm};
  color: ${props =>
    props.isError
      ? props.theme.colors.error[500]
      : props.theme.colors.neutral[500]};
`

export const Radio = forwardRef<HTMLInputElement, RadioProps>(
  (
    {
      size: sizeProp,
      colorScheme: colorSchemeProp,
      isDisabled: isDisabledProp,
      isInvalid: isInvalidProp,
      label,
      value,
      onChange,
      ...props
    },
    ref
  ) => {
    const group = useContext(RadioContext)

    const size = sizeProp || group.size
    const colorScheme = colorSchemeProp || group.colorScheme
    const isDisabled = isDisabledProp || group.isDisabled
    const isInvalid = isInvalidProp || group.isInvalid

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      if (group.onChange) {
        group.onChange(event.target.value)
      }
      if (onChange) {
        onChange(event)
      }
    }

    return (
      <RadioContainer isDisabled={isDisabled}>
        <HiddenRadio
          ref={ref}
          value={value}
          name={group.name}
          checked={group.value === value}
          disabled={isDisabled}
          required={group.isRequired}
          aria-invalid={isInvalid}
          onChange={handleChange}
          {...props}
        />
        <StyledRadio
          size={size}
          colorScheme={colorScheme}
          isChecked={group.value === value}
          isInvalid={isInvalid}
          isDisabled={isDisabled}
        >
          <RadioDot
            size={size}
            colorScheme={colorScheme}
          />
        </StyledRadio>
        {label && <LabelText size={size}>{label}</LabelText>}
      </RadioContainer>
    )
  }
)

export const RadioGroup = forwardRef<HTMLDivElement, RadioGroupProps>(
  (
    {
      children,
      name,
      size = 'md',
      colorScheme = 'primary',
      value,
      onChange,
      isDisabled = false,
      isRequired = false,
      isInvalid = false,
      helperText,
      errorMessage,
      label,
      direction = 'vertical',
      id,
      'aria-describedby': ariaDescribedBy,
      ...props
    },
    ref
  ) => {
    const [uniqueId] = useState(() => id || `radio-group-${Math.random().toString(36).substr(2, 9)}`)
    const helperId = `${uniqueId}-helper`
    const errorId = `${uniqueId}-error`

    const getAriaDescribedBy = useCallback(() => {
      const ids = []
      if (ariaDescribedBy) ids.push(ariaDescribedBy)
      if (helperText && !isInvalid) ids.push(helperId)
      if (errorMessage && isInvalid) ids.push(errorId)
      return ids.join(' ')
    }, [ariaDescribedBy, helperText, errorMessage, isInvalid, helperId, errorId])

    const context: RadioContextValue = {
      name,
      size,
      colorScheme,
      value,
      onChange,
      isDisabled,
      isRequired,
      isInvalid
    }

    return (
      <div>
        {label && <GroupLabel size={size}>{label}</GroupLabel>}
        <RadioContext.Provider value={context}>
          <RadioGroupContainer
            ref={ref}
            role="radiogroup"
            aria-invalid={isInvalid}
            aria-describedby={getAriaDescribedBy()}
            direction={direction}
            {...props}
          >
            {children}
          </RadioGroupContainer>
        </RadioContext.Provider>
        {(helperText || errorMessage) && (
          <HelperText
            id={isInvalid ? errorId : helperId}
            isError={isInvalid}
          >
            {isInvalid ? errorMessage : helperText}
          </HelperText>
        )}
      </div>
    )
  }
)

Radio.displayName = 'Radio'
RadioGroup.displayName = 'RadioGroup'

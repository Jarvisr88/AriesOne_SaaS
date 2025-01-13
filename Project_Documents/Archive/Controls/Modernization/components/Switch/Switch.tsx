import React, { useRef } from 'react'
import styled, { css } from 'styled-components'

export interface SwitchProps {
  /** If true, the switch is checked */
  isChecked?: boolean
  /** The default state of the switch */
  defaultChecked?: boolean
  /** If true, the switch is disabled */
  isDisabled?: boolean
  /** If true, the switch is required */
  isRequired?: boolean
  /** If true, the switch is invalid */
  isInvalid?: boolean
  /** The size of the switch */
  size?: 'sm' | 'md' | 'lg'
  /** The label of the switch */
  label?: string
  /** The color scheme of the switch */
  colorScheme?: 'primary' | 'success' | 'warning' | 'error'
  /** Called when the switch changes */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
  /** Name of the input field */
  name?: string
  /** Value of the input field */
  value?: string | number
  /** ID of the input field */
  id?: string
  /** Additional CSS class */
  className?: string
}

const sizes = {
  sm: {
    width: '28px',
    height: '16px',
    thumbSize: '12px'
  },
  md: {
    width: '36px',
    height: '20px',
    thumbSize: '16px'
  },
  lg: {
    width: '44px',
    height: '24px',
    thumbSize: '20px'
  }
}

const colorSchemes = {
  primary: css`
    --switch-color: ${props => props.theme.colors.primary[500]};
    --switch-hover-color: ${props => props.theme.colors.primary[600]};
  `,
  success: css`
    --switch-color: ${props => props.theme.colors.success[500]};
    --switch-hover-color: ${props => props.theme.colors.success[600]};
  `,
  warning: css`
    --switch-color: ${props => props.theme.colors.warning[500]};
    --switch-hover-color: ${props => props.theme.colors.warning[600]};
  `,
  error: css`
    --switch-color: ${props => props.theme.colors.error[500]};
    --switch-hover-color: ${props => props.theme.colors.error[600]};
  `
}

const SwitchContainer = styled.label<{
  size: 'sm' | 'md' | 'lg'
  isDisabled?: boolean
}>`
  display: inline-flex;
  align-items: center;
  position: relative;
  cursor: ${props => (props.isDisabled ? 'not-allowed' : 'pointer')};
  opacity: ${props => (props.isDisabled ? 0.6 : 1)};
  gap: ${props => props.theme.spacing.sm};
`

const SwitchTrack = styled.div<{
  size: 'sm' | 'md' | 'lg'
  colorScheme: 'primary' | 'success' | 'warning' | 'error'
  isChecked?: boolean
  isDisabled?: boolean
  isInvalid?: boolean
}>`
  ${props => colorSchemes[props.colorScheme]}
  position: relative;
  width: ${props => sizes[props.size].width};
  height: ${props => sizes[props.size].height};
  background-color: ${props =>
    props.isChecked
      ? 'var(--switch-color)'
      : props.theme.colors.neutral[300]};
  border-radius: ${props => props.theme.radii.full};
  transition: all 0.2s;

  &:hover {
    background-color: ${props =>
      props.isChecked && !props.isDisabled
        ? 'var(--switch-hover-color)'
        : props.theme.colors.neutral[400]};
  }

  ${props =>
    props.isInvalid &&
    css`
      border: 2px solid ${props.theme.colors.error[500]};
    `}
`

const SwitchThumb = styled.div<{
  size: 'sm' | 'md' | 'lg'
  isChecked?: boolean
}>`
  position: absolute;
  top: 2px;
  left: 2px;
  width: ${props => sizes[props.size].thumbSize};
  height: ${props => sizes[props.size].thumbSize};
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.radii.full};
  box-shadow: ${props => props.theme.shadows.sm};
  transition: transform 0.2s;
  transform: ${props =>
    props.isChecked
      ? `translateX(calc(${sizes[props.size].width} - ${
          sizes[props.size].thumbSize
        } - 4px))`
      : 'translateX(0)'};
`

const HiddenInput = styled.input`
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
`

const SwitchLabel = styled.span<{
  size: 'sm' | 'md' | 'lg'
}>`
  font-size: ${props =>
    props.size === 'lg'
      ? props.theme.fontSizes.md
      : props.theme.fontSizes.sm};
  color: ${props => props.theme.colors.neutral[900]};
`

export const Switch: React.FC<SwitchProps> = ({
  isChecked,
  defaultChecked,
  isDisabled,
  isRequired,
  isInvalid,
  size = 'md',
  label,
  colorScheme = 'primary',
  onChange,
  name,
  value,
  id,
  className
}) => {
  const inputRef = useRef<HTMLInputElement>(null)
  const [checked, setChecked] = React.useState(
    isChecked !== undefined ? isChecked : defaultChecked || false
  )

  React.useEffect(() => {
    if (isChecked !== undefined) {
      setChecked(isChecked)
    }
  }, [isChecked])

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (isChecked === undefined) {
      setChecked(event.target.checked)
    }
    onChange?.(event)
  }

  const handleClick = () => {
    inputRef.current?.click()
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === ' ' || event.key === 'Enter') {
      event.preventDefault()
      inputRef.current?.click()
    }
  }

  return (
    <SwitchContainer
      size={size}
      isDisabled={isDisabled}
      className={className}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={isDisabled ? -1 : 0}
      role="switch"
      aria-checked={checked}
      aria-disabled={isDisabled}
      aria-required={isRequired}
      aria-invalid={isInvalid}
    >
      <HiddenInput
        ref={inputRef}
        type="checkbox"
        name={name}
        value={value}
        id={id}
        checked={checked}
        defaultChecked={defaultChecked}
        disabled={isDisabled}
        required={isRequired}
        onChange={handleChange}
        aria-invalid={isInvalid}
      />
      <SwitchTrack
        size={size}
        colorScheme={colorScheme}
        isChecked={checked}
        isDisabled={isDisabled}
        isInvalid={isInvalid}
      >
        <SwitchThumb size={size} isChecked={checked} />
      </SwitchTrack>
      {label && <SwitchLabel size={size}>{label}</SwitchLabel>}
    </SwitchContainer>
  )
}

Switch.displayName = 'Switch'

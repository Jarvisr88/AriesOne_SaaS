import React, { forwardRef } from 'react'
import styled, { css } from 'styled-components'
import { Theme } from '../../theme/theme'

export type ButtonVariant = 'solid' | 'outline' | 'ghost' | 'link'
export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
export type ButtonColorScheme = 'primary' | 'success' | 'warning' | 'error' | 'neutral'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** The visual variant of the button */
  variant?: ButtonVariant
  /** The size of the button */
  size?: ButtonSize
  /** The color scheme of the button */
  colorScheme?: ButtonColorScheme
  /** If true, the button will be disabled */
  isDisabled?: boolean
  /** If true, the button will show a loading spinner */
  isLoading?: boolean
  /** If true, the button will take up the full width of its container */
  isFullWidth?: boolean
  /** The icon to show before the button text */
  leftIcon?: React.ReactElement
  /** The icon to show after the button text */
  rightIcon?: React.ReactElement
  /** The space between the button icon and label */
  iconSpacing?: keyof Theme['spacing']
}

const sizeStyles = {
  xs: css`
    height: 1.5rem;
    min-width: 1.5rem;
    font-size: ${props => props.theme.fontSizes.xs};
    padding-left: ${props => props.theme.spacing.xs};
    padding-right: ${props => props.theme.spacing.xs};
  `,
  sm: css`
    height: 2rem;
    min-width: 2rem;
    font-size: ${props => props.theme.fontSizes.sm};
    padding-left: ${props => props.theme.spacing.sm};
    padding-right: ${props => props.theme.spacing.sm};
  `,
  md: css`
    height: 2.5rem;
    min-width: 2.5rem;
    font-size: ${props => props.theme.fontSizes.md};
    padding-left: ${props => props.theme.spacing.md};
    padding-right: ${props => props.theme.spacing.md};
  `,
  lg: css`
    height: 3rem;
    min-width: 3rem;
    font-size: ${props => props.theme.fontSizes.lg};
    padding-left: ${props => props.theme.spacing.lg};
    padding-right: ${props => props.theme.spacing.lg};
  `,
  xl: css`
    height: 3.5rem;
    min-width: 3.5rem;
    font-size: ${props => props.theme.fontSizes.xl};
    padding-left: ${props => props.theme.spacing.xl};
    padding-right: ${props => props.theme.spacing.xl};
  `
}

const variantStyles = {
  solid: (props: any) => css`
    background-color: ${props.theme.colors[props.colorScheme][500]};
    color: ${props.theme.colors.white};

    &:hover:not(:disabled) {
      background-color: ${props.theme.colors[props.colorScheme][600]};
    }

    &:active:not(:disabled) {
      background-color: ${props.theme.colors[props.colorScheme][700]};
    }

    &:focus-visible {
      box-shadow: 0 0 0 3px ${props.theme.colors[props.colorScheme][200]};
    }
  `,
  outline: (props: any) => css`
    background-color: transparent;
    border: 1px solid ${props.theme.colors[props.colorScheme][500]};
    color: ${props.theme.colors[props.colorScheme][500]};

    &:hover:not(:disabled) {
      background-color: ${props.theme.colors[props.colorScheme][50]};
    }

    &:active:not(:disabled) {
      background-color: ${props.theme.colors[props.colorScheme][100]};
    }

    &:focus-visible {
      box-shadow: 0 0 0 3px ${props.theme.colors[props.colorScheme][200]};
    }
  `,
  ghost: (props: any) => css`
    background-color: transparent;
    color: ${props.theme.colors[props.colorScheme][500]};

    &:hover:not(:disabled) {
      background-color: ${props.theme.colors[props.colorScheme][50]};
    }

    &:active:not(:disabled) {
      background-color: ${props.theme.colors[props.colorScheme][100]};
    }

    &:focus-visible {
      box-shadow: 0 0 0 3px ${props.theme.colors[props.colorScheme][200]};
    }
  `,
  link: (props: any) => css`
    background-color: transparent;
    color: ${props.theme.colors[props.colorScheme][500]};
    padding: 0;
    height: auto;
    min-width: 0;

    &:hover:not(:disabled) {
      text-decoration: underline;
    }

    &:focus-visible {
      box-shadow: 0 0 0 3px ${props.theme.colors[props.colorScheme][200]};
    }
  `
}

const StyledButton = styled.button<ButtonProps>`
  /* Base styles */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
  white-space: nowrap;
  vertical-align: middle;
  border-radius: ${props => props.theme.radii.md};
  font-weight: ${props => props.theme.fontWeights.semibold};
  transition: ${props => props.theme.transitions.default};
  cursor: pointer;
  border: none;
  outline: none;
  line-height: 1.2;
  -webkit-appearance: none;
  -webkit-tap-highlight-color: transparent;

  /* Size styles */
  ${props => sizeStyles[props.size || 'md']}

  /* Variant styles */
  ${props => variantStyles[props.variant || 'solid'](props)}

  /* Full width styles */
  ${props =>
    props.isFullWidth &&
    css`
      width: 100%;
    `}

  /* Disabled styles */
  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    box-shadow: none;
  }

  /* Loading styles */
  ${props =>
    props.isLoading &&
    css`
      cursor: wait;

      & > *:not(.loading-spinner) {
        opacity: 0;
      }
    `}

  /* Focus styles */
  &:focus-visible {
    outline: none;
  }
`

const ButtonContent = styled.span<{ hasLeftIcon?: boolean; hasRightIcon?: boolean; iconSpacing?: string }>`
  display: flex;
  align-items: center;
  justify-content: center;

  ${props =>
    props.hasLeftIcon &&
    css`
      & > *:first-child {
        margin-right: ${props.iconSpacing || props.theme.spacing.xs};
      }
    `}

  ${props =>
    props.hasRightIcon &&
    css`
      & > *:last-child {
        margin-left: ${props.iconSpacing || props.theme.spacing.xs};
      }
    `}
`

const LoadingSpinner = styled.div`
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;

  &::after {
    content: '';
    width: 1em;
    height: 1em;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
`

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'solid',
      size = 'md',
      colorScheme = 'primary',
      isDisabled = false,
      isLoading = false,
      isFullWidth = false,
      leftIcon,
      rightIcon,
      iconSpacing,
      ...props
    },
    ref
  ) => {
    return (
      <StyledButton
        ref={ref}
        variant={variant}
        size={size}
        colorScheme={colorScheme}
        disabled={isDisabled || isLoading}
        isLoading={isLoading}
        isFullWidth={isFullWidth}
        {...props}
      >
        {isLoading && <LoadingSpinner className="loading-spinner" />}
        <ButtonContent
          hasLeftIcon={!!leftIcon}
          hasRightIcon={!!rightIcon}
          iconSpacing={iconSpacing}
        >
          {leftIcon}
          {children}
          {rightIcon}
        </ButtonContent>
      </StyledButton>
    )
  }
)

Button.displayName = 'Button'

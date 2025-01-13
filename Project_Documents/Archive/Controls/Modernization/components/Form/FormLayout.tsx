import React from 'react'
import styled from 'styled-components'

export interface FormLayoutProps {
  /** The layout direction */
  direction?: 'vertical' | 'horizontal'
  /** The spacing between form elements */
  spacing?: 'sm' | 'md' | 'lg'
  /** The maximum width of the form */
  maxWidth?: string
  /** The alignment of form elements */
  align?: 'start' | 'center' | 'end'
  /** Children elements */
  children: React.ReactNode
  /** Additional CSS class */
  className?: string
}

const getSpacing = (spacing: string) => {
  const spacings = {
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem'
  }
  return spacings[spacing] || '1rem'
}

const FormLayoutContainer = styled.div<{
  direction: 'vertical' | 'horizontal'
  spacing: string
  maxWidth?: string
  align: string
}>`
  display: flex;
  flex-direction: ${props => props.direction === 'horizontal' ? 'row' : 'column'};
  gap: ${props => getSpacing(props.spacing)};
  width: 100%;
  max-width: ${props => props.maxWidth};
  align-items: ${props => props.align};

  @media (max-width: ${props => props.theme.breakpoints.sm}) {
    flex-direction: column;
  }
`

const FormRow = styled.div<{ spacing: string }>`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => getSpacing(props.spacing)};
  width: 100%;
`

const FormColumn = styled.div<{ width?: string }>`
  flex: ${props => props.width ? 'none' : '1'};
  width: ${props => props.width};
  min-width: 0;
`

export interface FormRowProps {
  /** The spacing between columns */
  spacing?: 'sm' | 'md' | 'lg'
  /** Children elements */
  children: React.ReactNode
  /** Additional CSS class */
  className?: string
}

export interface FormColumnProps {
  /** The width of the column */
  width?: string
  /** Children elements */
  children: React.ReactNode
  /** Additional CSS class */
  className?: string
}

export const FormLayout: React.FC<FormLayoutProps> & {
  Row: React.FC<FormRowProps>
  Column: React.FC<FormColumnProps>
} = ({
  direction = 'vertical',
  spacing = 'md',
  maxWidth,
  align = 'start',
  children,
  className
}) => {
  return (
    <FormLayoutContainer
      direction={direction}
      spacing={spacing}
      maxWidth={maxWidth}
      align={align}
      className={className}
    >
      {children}
    </FormLayoutContainer>
  )
}

FormLayout.Row = ({ spacing = 'md', children, className }) => (
  <FormRow spacing={spacing} className={className}>
    {children}
  </FormRow>
)

FormLayout.Column = ({ width, children, className }) => (
  <FormColumn width={width} className={className}>
    {children}
  </FormColumn>
)

FormLayout.displayName = 'FormLayout'
FormLayout.Row.displayName = 'FormLayout.Row'
FormLayout.Column.displayName = 'FormLayout.Column'

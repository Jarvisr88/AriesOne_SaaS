import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Input } from './Input'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Input', () => {
  it('renders correctly', () => {
    renderWithTheme(<Input aria-label="test-input" />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('renders with label', () => {
    renderWithTheme(<Input label="Username" />)
    expect(screen.getByLabelText('Username')).toBeInTheDocument()
  })

  it('shows required indicator when isRequired is true', () => {
    renderWithTheme(<Input label="Username" isRequired />)
    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('shows helper text when provided', () => {
    renderWithTheme(<Input helperText="Enter your username" />)
    expect(screen.getByText('Enter your username')).toBeInTheDocument()
  })

  it('shows error message when invalid', () => {
    renderWithTheme(
      <Input
        isInvalid
        errorMessage="Username is required"
      />
    )
    expect(screen.getByText('Username is required')).toBeInTheDocument()
  })

  it('handles value changes', () => {
    const handleChange = jest.fn()
    renderWithTheme(
      <Input
        value="test"
        onChange={handleChange}
        aria-label="test-input"
      />
    )
    
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'new value' } })
    expect(handleChange).toHaveBeenCalled()
  })

  it('disables the input when isDisabled is true', () => {
    renderWithTheme(<Input isDisabled aria-label="test-input" />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  it('makes the input readonly when isReadOnly is true', () => {
    renderWithTheme(<Input isReadOnly aria-label="test-input" />)
    expect(screen.getByRole('textbox')).toHaveAttribute('readonly')
  })

  it('renders with left icon', () => {
    renderWithTheme(
      <Input
        leftIcon={<span data-testid="left-icon">🔍</span>}
        aria-label="test-input"
      />
    )
    expect(screen.getByTestId('left-icon')).toBeInTheDocument()
  })

  it('renders with right icon', () => {
    renderWithTheme(
      <Input
        rightIcon={<span data-testid="right-icon">✓</span>}
        aria-label="test-input"
      />
    )
    expect(screen.getByTestId('right-icon')).toBeInTheDocument()
  })

  it('renders with addons', () => {
    renderWithTheme(
      <Input
        leftAddon="https://"
        rightAddon=".com"
        aria-label="test-input"
      />
    )
    expect(screen.getByText('https://')).toBeInTheDocument()
    expect(screen.getByText('.com')).toBeInTheDocument()
  })

  it('applies different sizes correctly', () => {
    const { rerender } = renderWithTheme(
      <Input size="sm" aria-label="test-input" />
    )
    expect(screen.getByRole('textbox')).toHaveStyle({ height: '2rem' })

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Input size="lg" aria-label="test-input" />
      </ThemeProvider>
    )
    expect(screen.getByRole('textbox')).toHaveStyle({ height: '3rem' })
  })

  it('applies different variants correctly', () => {
    const { rerender } = renderWithTheme(
      <Input variant="filled" aria-label="test-input" />
    )
    expect(screen.getByRole('textbox')).toHaveStyle({
      backgroundColor: lightTheme.colors.neutral[100]
    })

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Input variant="flushed" aria-label="test-input" />
      </ThemeProvider>
    )
    expect(screen.getByRole('textbox')).toHaveStyle({ borderRadius: '0' })
  })

  it('is accessible using keyboard', () => {
    renderWithTheme(<Input aria-label="test-input" />)
    const input = screen.getByRole('textbox')
    
    input.focus()
    expect(input).toHaveFocus()
    
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(input).toHaveFocus()
  })

  it('associates helper text with input using aria-describedby', () => {
    renderWithTheme(
      <Input
        helperText="Helper text"
        aria-label="test-input"
      />
    )
    const input = screen.getByRole('textbox')
    const helperText = screen.getByText('Helper text')
    
    expect(input).toHaveAttribute(
      'aria-describedby',
      helperText.getAttribute('id')
    )
  })

  it('associates error message with input using aria-describedby when invalid', () => {
    renderWithTheme(
      <Input
        isInvalid
        errorMessage="Error message"
        aria-label="test-input"
      />
    )
    const input = screen.getByRole('textbox')
    const errorMessage = screen.getByText('Error message')
    
    expect(input).toHaveAttribute(
      'aria-describedby',
      errorMessage.getAttribute('id')
    )
    expect(input).toHaveAttribute('aria-invalid', 'true')
  })
})

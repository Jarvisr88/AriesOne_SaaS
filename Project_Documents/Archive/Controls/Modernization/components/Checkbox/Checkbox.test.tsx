import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Checkbox } from './Checkbox'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Checkbox', () => {
  it('renders correctly', () => {
    renderWithTheme(<Checkbox aria-label="test-checkbox" />)
    expect(screen.getByRole('checkbox')).toBeInTheDocument()
  })

  it('renders with label', () => {
    renderWithTheme(<Checkbox label="Accept terms" />)
    expect(screen.getByLabelText('Accept terms')).toBeInTheDocument()
  })

  it('shows helper text when provided', () => {
    renderWithTheme(
      <Checkbox
        helperText="Please accept the terms"
      />
    )
    expect(screen.getByText('Please accept the terms')).toBeInTheDocument()
  })

  it('shows error message when invalid', () => {
    renderWithTheme(
      <Checkbox
        isInvalid
        errorMessage="This field is required"
      />
    )
    expect(screen.getByText('This field is required')).toBeInTheDocument()
  })

  it('handles checked state changes', () => {
    const handleChange = jest.fn()
    renderWithTheme(
      <Checkbox
        onChange={handleChange}
        aria-label="test-checkbox"
      />
    )
    
    const checkbox = screen.getByRole('checkbox')
    fireEvent.click(checkbox)
    expect(handleChange).toHaveBeenCalled()
    expect(checkbox).toBeChecked()
  })

  it('handles indeterminate state', () => {
    renderWithTheme(
      <Checkbox
        isIndeterminate
        aria-label="test-checkbox"
      />
    )
    
    const checkbox = screen.getByRole('checkbox')
    expect(checkbox).toHaveProperty('indeterminate', true)
  })

  it('disables the checkbox when isDisabled is true', () => {
    renderWithTheme(
      <Checkbox
        isDisabled
        aria-label="test-checkbox"
      />
    )
    expect(screen.getByRole('checkbox')).toBeDisabled()
  })

  it('makes the checkbox readonly when isReadOnly is true', () => {
    const handleChange = jest.fn()
    renderWithTheme(
      <Checkbox
        isReadOnly
        onChange={handleChange}
        aria-label="test-checkbox"
      />
    )
    
    const checkbox = screen.getByRole('checkbox')
    fireEvent.click(checkbox)
    expect(handleChange).not.toHaveBeenCalled()
  })

  it('applies different sizes correctly', () => {
    const { rerender } = renderWithTheme(
      <Checkbox size="sm" aria-label="test-checkbox" />
    )
    let checkbox = screen.getByRole('checkbox')
    expect(checkbox.nextSibling).toHaveStyle({ width: '1.25rem' })

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Checkbox size="lg" aria-label="test-checkbox" />
      </ThemeProvider>
    )
    checkbox = screen.getByRole('checkbox')
    expect(checkbox.nextSibling).toHaveStyle({ width: '1.75rem' })
  })

  it('applies different color schemes correctly', () => {
    renderWithTheme(
      <Checkbox
        colorScheme="success"
        defaultChecked
        aria-label="test-checkbox"
      />
    )
    const checkbox = screen.getByRole('checkbox')
    expect(checkbox.nextSibling).toHaveStyle({
      backgroundColor: lightTheme.colors.success[500]
    })
  })

  it('is accessible using keyboard', () => {
    renderWithTheme(<Checkbox aria-label="test-checkbox" />)
    const checkbox = screen.getByRole('checkbox')
    
    checkbox.focus()
    expect(checkbox).toHaveFocus()
    
    fireEvent.keyDown(checkbox, { key: ' ' })
    expect(checkbox).toBeChecked()
  })

  it('associates helper text with checkbox using aria-describedby', () => {
    renderWithTheme(
      <Checkbox
        helperText="Helper text"
        aria-label="test-checkbox"
      />
    )
    const checkbox = screen.getByRole('checkbox')
    const helperText = screen.getByText('Helper text')
    
    expect(checkbox).toHaveAttribute(
      'aria-describedby',
      helperText.getAttribute('id')
    )
  })

  it('associates error message with checkbox using aria-describedby when invalid', () => {
    renderWithTheme(
      <Checkbox
        isInvalid
        errorMessage="Error message"
        aria-label="test-checkbox"
      />
    )
    const checkbox = screen.getByRole('checkbox')
    const errorMessage = screen.getByText('Error message')
    
    expect(checkbox).toHaveAttribute(
      'aria-describedby',
      errorMessage.getAttribute('id')
    )
    expect(checkbox).toHaveAttribute('aria-invalid', 'true')
  })

  it('maintains controlled state correctly', () => {
    const { rerender } = renderWithTheme(
      <Checkbox
        checked={true}
        onChange={() => {}}
        aria-label="test-checkbox"
      />
    )
    expect(screen.getByRole('checkbox')).toBeChecked()

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Checkbox
          checked={false}
          onChange={() => {}}
          aria-label="test-checkbox"
        />
      </ThemeProvider>
    )
    expect(screen.getByRole('checkbox')).not.toBeChecked()
  })
})

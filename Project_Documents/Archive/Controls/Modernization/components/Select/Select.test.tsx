import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Select } from './Select'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

const mockOptions = [
  { value: 'option1', label: 'Option 1' },
  { value: 'option2', label: 'Option 2' },
  { value: 'option3', label: 'Option 3', isDisabled: true }
]

describe('Select', () => {
  it('renders correctly', () => {
    renderWithTheme(<Select options={mockOptions} aria-label="test-select" />)
    expect(screen.getByRole('combobox')).toBeInTheDocument()
  })

  it('renders with label', () => {
    renderWithTheme(<Select options={mockOptions} label="Choose an option" />)
    expect(screen.getByLabelText('Choose an option')).toBeInTheDocument()
  })

  it('shows required indicator when isRequired is true', () => {
    renderWithTheme(<Select options={mockOptions} label="Choose an option" isRequired />)
    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('shows helper text when provided', () => {
    renderWithTheme(
      <Select
        options={mockOptions}
        helperText="Please select an option"
      />
    )
    expect(screen.getByText('Please select an option')).toBeInTheDocument()
  })

  it('shows error message when invalid', () => {
    renderWithTheme(
      <Select
        options={mockOptions}
        isInvalid
        errorMessage="Selection is required"
      />
    )
    expect(screen.getByText('Selection is required')).toBeInTheDocument()
  })

  it('handles value changes', () => {
    const handleChange = jest.fn()
    renderWithTheme(
      <Select
        options={mockOptions}
        onChange={handleChange}
        aria-label="test-select"
      />
    )
    
    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'option1' } })
    expect(handleChange).toHaveBeenCalledWith('option1')
  })

  it('handles multiple selection', () => {
    const handleChange = jest.fn()
    renderWithTheme(
      <Select
        options={mockOptions}
        isMulti
        onChange={handleChange}
        aria-label="test-select"
      />
    )
    
    const select = screen.getByRole('listbox')
    fireEvent.change(select, {
      target: {
        selectedOptions: [
          { value: 'option1' },
          { value: 'option2' }
        ]
      }
    })
    expect(handleChange).toHaveBeenCalledWith(['option1', 'option2'])
  })

  it('disables the select when isDisabled is true', () => {
    renderWithTheme(
      <Select
        options={mockOptions}
        isDisabled
        aria-label="test-select"
      />
    )
    expect(screen.getByRole('combobox')).toBeDisabled()
  })

  it('renders disabled options', () => {
    renderWithTheme(<Select options={mockOptions} aria-label="test-select" />)
    const options = screen.getAllByRole('option')
    expect(options[2]).toHaveAttribute('disabled')
  })

  it('shows placeholder when provided', () => {
    renderWithTheme(
      <Select
        options={mockOptions}
        placeholder="Select an option"
        aria-label="test-select"
      />
    )
    expect(screen.getByText('Select an option')).toBeInTheDocument()
  })

  it('applies different sizes correctly', () => {
    const { rerender } = renderWithTheme(
      <Select options={mockOptions} size="sm" aria-label="test-select" />
    )
    expect(screen.getByRole('combobox')).toHaveStyle({ height: '2rem' })

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Select options={mockOptions} size="lg" aria-label="test-select" />
      </ThemeProvider>
    )
    expect(screen.getByRole('combobox')).toHaveStyle({ height: '3rem' })
  })

  it('applies different variants correctly', () => {
    const { rerender } = renderWithTheme(
      <Select options={mockOptions} variant="filled" aria-label="test-select" />
    )
    expect(screen.getByRole('combobox')).toHaveStyle({
      backgroundColor: lightTheme.colors.neutral[100]
    })

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Select options={mockOptions} variant="flushed" aria-label="test-select" />
      </ThemeProvider>
    )
    expect(screen.getByRole('combobox')).toHaveStyle({ borderRadius: '0' })
  })

  it('is accessible using keyboard', () => {
    renderWithTheme(<Select options={mockOptions} aria-label="test-select" />)
    const select = screen.getByRole('combobox')
    
    select.focus()
    expect(select).toHaveFocus()
    
    fireEvent.keyDown(select, { key: 'ArrowDown' })
    expect(select).toHaveFocus()
  })

  it('associates helper text with select using aria-describedby', () => {
    renderWithTheme(
      <Select
        options={mockOptions}
        helperText="Helper text"
        aria-label="test-select"
      />
    )
    const select = screen.getByRole('combobox')
    const helperText = screen.getByText('Helper text')
    
    expect(select).toHaveAttribute(
      'aria-describedby',
      helperText.getAttribute('id')
    )
  })

  it('associates error message with select using aria-describedby when invalid', () => {
    renderWithTheme(
      <Select
        options={mockOptions}
        isInvalid
        errorMessage="Error message"
        aria-label="test-select"
      />
    )
    const select = screen.getByRole('combobox')
    const errorMessage = screen.getByText('Error message')
    
    expect(select).toHaveAttribute(
      'aria-describedby',
      errorMessage.getAttribute('id')
    )
    expect(select).toHaveAttribute('aria-invalid', 'true')
  })
})

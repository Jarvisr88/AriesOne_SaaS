import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Radio, RadioGroup } from './Radio'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Radio and RadioGroup', () => {
  describe('Radio', () => {
    it('renders correctly', () => {
      renderWithTheme(<Radio value="test" aria-label="test-radio" />)
      expect(screen.getByRole('radio')).toBeInTheDocument()
    })

    it('renders with label', () => {
      renderWithTheme(<Radio value="test" label="Test Option" />)
      expect(screen.getByLabelText('Test Option')).toBeInTheDocument()
    })

    it('can be disabled', () => {
      renderWithTheme(<Radio value="test" isDisabled aria-label="test-radio" />)
      expect(screen.getByRole('radio')).toBeDisabled()
    })

    it('applies different sizes correctly', () => {
      const { rerender } = renderWithTheme(
        <Radio size="sm" value="test" aria-label="test-radio" />
      )
      let radio = screen.getByRole('radio')
      expect(radio.nextSibling).toHaveStyle({ width: '1.25rem' })

      rerender(
        <ThemeProvider theme={lightTheme}>
          <Radio size="lg" value="test" aria-label="test-radio" />
        </ThemeProvider>
      )
      radio = screen.getByRole('radio')
      expect(radio.nextSibling).toHaveStyle({ width: '1.75rem' })
    })
  })

  describe('RadioGroup', () => {
    const options = [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2' },
      { value: 'option3', label: 'Option 3' }
    ]

    it('renders correctly with options', () => {
      renderWithTheme(
        <RadioGroup name="test-group">
          {options.map(option => (
            <Radio
              key={option.value}
              value={option.value}
              label={option.label}
            />
          ))}
        </RadioGroup>
      )
      expect(screen.getAllByRole('radio')).toHaveLength(3)
    })

    it('renders with group label', () => {
      renderWithTheme(
        <RadioGroup name="test-group" label="Test Group">
          {options.map(option => (
            <Radio
              key={option.value}
              value={option.value}
              label={option.label}
            />
          ))}
        </RadioGroup>
      )
      expect(screen.getByText('Test Group')).toBeInTheDocument()
    })

    it('shows helper text when provided', () => {
      renderWithTheme(
        <RadioGroup
          name="test-group"
          helperText="Please select an option"
        >
          {options.map(option => (
            <Radio
              key={option.value}
              value={option.value}
              label={option.label}
            />
          ))}
        </RadioGroup>
      )
      expect(screen.getByText('Please select an option')).toBeInTheDocument()
    })

    it('shows error message when invalid', () => {
      renderWithTheme(
        <RadioGroup
          name="test-group"
          isInvalid
          errorMessage="Selection is required"
        >
          {options.map(option => (
            <Radio
              key={option.value}
              value={option.value}
              label={option.label}
            />
          ))}
        </RadioGroup>
      )
      expect(screen.getByText('Selection is required')).toBeInTheDocument()
    })

    it('handles value changes', () => {
      const handleChange = jest.fn()
      renderWithTheme(
        <RadioGroup name="test-group" onChange={handleChange}>
          {options.map(option => (
            <Radio
              key={option.value}
              value={option.value}
              label={option.label}
            />
          ))}
        </RadioGroup>
      )
      
      fireEvent.click(screen.getByLabelText('Option 1'))
      expect(handleChange).toHaveBeenCalledWith('option1')
    })

    it('maintains controlled state correctly', () => {
      const { rerender } = renderWithTheme(
        <RadioGroup name="test-group" value="option1">
          {options.map(option => (
            <Radio
              key={option.value}
              value={option.value}
              label={option.label}
            />
          ))}
        </RadioGroup>
      )

      expect(screen.getByLabelText('Option 1')).toBeChecked()

      rerender(
        <ThemeProvider theme={lightTheme}>
          <RadioGroup name="test-group" value="option2">
            {options.map(option => (
              <Radio
                key={option.value}
                value={option.value}
                label={option.label}
              />
            ))}
          </RadioGroup>
        </ThemeProvider>
      )

      expect(screen.getByLabelText('Option 2')).toBeChecked()
    })

    it('disables all radios when group is disabled', () => {
      renderWithTheme(
        <RadioGroup name="test-group" isDisabled>
          {options.map(option => (
            <Radio
              key={option.value}
              value={option.value}
              label={option.label}
            />
          ))}
        </RadioGroup>
      )
      screen.getAllByRole('radio').forEach(radio => {
        expect(radio).toBeDisabled()
      })
    })

    it('applies different layouts based on direction prop', () => {
      const { rerender } = renderWithTheme(
        <RadioGroup name="test-group" direction="vertical">
          {options.map(option => (
            <Radio
              key={option.value}
              value={option.value}
              label={option.label}
            />
          ))}
        </RadioGroup>
      )
      expect(screen.getByRole('radiogroup')).toHaveStyle({
        flexDirection: 'column'
      })

      rerender(
        <ThemeProvider theme={lightTheme}>
          <RadioGroup name="test-group" direction="horizontal">
            {options.map(option => (
              <Radio
                key={option.value}
                value={option.value}
                label={option.label}
              />
            ))}
          </RadioGroup>
        </ThemeProvider>
      )
      expect(screen.getByRole('radiogroup')).toHaveStyle({
        flexDirection: 'row'
      })
    })

    it('is accessible using keyboard', () => {
      renderWithTheme(
        <RadioGroup name="test-group">
          {options.map(option => (
            <Radio
              key={option.value}
              value={option.value}
              label={option.label}
            />
          ))}
        </RadioGroup>
      )
      
      const firstRadio = screen.getByLabelText('Option 1')
      firstRadio.focus()
      expect(firstRadio).toHaveFocus()
      
      fireEvent.keyDown(firstRadio, { key: ' ' })
      expect(firstRadio).toBeChecked()
    })

    it('associates helper text with group using aria-describedby', () => {
      renderWithTheme(
        <RadioGroup
          name="test-group"
          helperText="Helper text"
        >
          {options.map(option => (
            <Radio
              key={option.value}
              value={option.value}
              label={option.label}
            />
          ))}
        </RadioGroup>
      )
      const group = screen.getByRole('radiogroup')
      const helperText = screen.getByText('Helper text')
      
      expect(group).toHaveAttribute(
        'aria-describedby',
        helperText.getAttribute('id')
      )
    })
  })
})

import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Switch } from './Switch'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Switch', () => {
  it('renders switch with label', () => {
    renderWithTheme(<Switch label="Test Switch" />)
    expect(screen.getByText('Test Switch')).toBeInTheDocument()
  })

  it('renders switch without label', () => {
    renderWithTheme(<Switch />)
    expect(screen.getByRole('switch')).toBeInTheDocument()
  })

  it('handles controlled state', () => {
    const onChange = jest.fn()
    renderWithTheme(
      <Switch isChecked={true} onChange={onChange} label="Test Switch" />
    )

    const switchElement = screen.getByRole('switch')
    expect(switchElement).toHaveAttribute('aria-checked', 'true')

    fireEvent.click(switchElement)
    expect(onChange).toHaveBeenCalled()
    expect(switchElement).toHaveAttribute('aria-checked', 'true')
  })

  it('handles uncontrolled state', () => {
    renderWithTheme(<Switch defaultChecked label="Test Switch" />)

    const switchElement = screen.getByRole('switch')
    expect(switchElement).toHaveAttribute('aria-checked', 'true')

    fireEvent.click(switchElement)
    expect(switchElement).toHaveAttribute('aria-checked', 'false')
  })

  it('handles disabled state', () => {
    const onChange = jest.fn()
    renderWithTheme(
      <Switch isDisabled onChange={onChange} label="Test Switch" />
    )

    const switchElement = screen.getByRole('switch')
    expect(switchElement).toHaveAttribute('aria-disabled', 'true')
    expect(switchElement).toHaveAttribute('tabindex', '-1')

    fireEvent.click(switchElement)
    expect(onChange).not.toHaveBeenCalled()
  })

  it('handles required state', () => {
    renderWithTheme(<Switch isRequired label="Test Switch" />)

    const switchElement = screen.getByRole('switch')
    expect(switchElement).toHaveAttribute('aria-required', 'true')
  })

  it('handles invalid state', () => {
    renderWithTheme(<Switch isInvalid label="Test Switch" />)

    const switchElement = screen.getByRole('switch')
    expect(switchElement).toHaveAttribute('aria-invalid', 'true')
  })

  it('handles keyboard interaction', () => {
    const onChange = jest.fn()
    renderWithTheme(<Switch onChange={onChange} label="Test Switch" />)

    const switchElement = screen.getByRole('switch')
    switchElement.focus()

    fireEvent.keyDown(switchElement, { key: ' ' })
    expect(onChange).toHaveBeenCalled()
    expect(switchElement).toHaveAttribute('aria-checked', 'true')

    fireEvent.keyDown(switchElement, { key: 'Enter' })
    expect(onChange).toHaveBeenCalledTimes(2)
    expect(switchElement).toHaveAttribute('aria-checked', 'false')
  })

  it('handles different sizes', () => {
    const { rerender } = renderWithTheme(
      <Switch size="sm" label="Test Switch" />
    )
    expect(screen.getByRole('switch')).toBeInTheDocument()

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Switch size="md" label="Test Switch" />
      </ThemeProvider>
    )
    expect(screen.getByRole('switch')).toBeInTheDocument()

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Switch size="lg" label="Test Switch" />
      </ThemeProvider>
    )
    expect(screen.getByRole('switch')).toBeInTheDocument()
  })

  it('handles different color schemes', () => {
    const { rerender } = renderWithTheme(
      <Switch colorScheme="primary" label="Test Switch" />
    )
    expect(screen.getByRole('switch')).toBeInTheDocument()

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Switch colorScheme="success" label="Test Switch" />
      </ThemeProvider>
    )
    expect(screen.getByRole('switch')).toBeInTheDocument()

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Switch colorScheme="warning" label="Test Switch" />
      </ThemeProvider>
    )
    expect(screen.getByRole('switch')).toBeInTheDocument()

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Switch colorScheme="error" label="Test Switch" />
      </ThemeProvider>
    )
    expect(screen.getByRole('switch')).toBeInTheDocument()
  })

  it('passes through name, value, and id props', () => {
    renderWithTheme(
      <Switch
        name="test-name"
        value="test-value"
        id="test-id"
        label="Test Switch"
      />
    )

    const input = screen.getByRole('checkbox')
    expect(input).toHaveAttribute('name', 'test-name')
    expect(input).toHaveAttribute('value', 'test-value')
    expect(input).toHaveAttribute('id', 'test-id')
  })

  it('passes through className prop', () => {
    renderWithTheme(
      <Switch className="test-class" label="Test Switch" />
    )

    expect(screen.getByRole('switch')).toHaveClass('test-class')
  })
})

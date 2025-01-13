import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Button } from './Button'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Button', () => {
  it('renders correctly', () => {
    renderWithTheme(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toHaveTextContent('Click me')
  })

  it('handles click events', () => {
    const handleClick = jest.fn()
    renderWithTheme(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('disables the button when isDisabled is true', () => {
    renderWithTheme(<Button isDisabled>Click me</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('shows loading state when isLoading is true', () => {
    renderWithTheme(<Button isLoading>Click me</Button>)
    expect(screen.getByRole('button')).toHaveAttribute('disabled')
    expect(screen.getByRole('button')).toContainElement(
      document.querySelector('.loading-spinner')
    )
  })

  it('renders with left icon', () => {
    renderWithTheme(
      <Button leftIcon={<span data-testid="left-icon">←</span>}>
        Click me
      </Button>
    )
    expect(screen.getByTestId('left-icon')).toBeInTheDocument()
  })

  it('renders with right icon', () => {
    renderWithTheme(
      <Button rightIcon={<span data-testid="right-icon">→</span>}>
        Click me
      </Button>
    )
    expect(screen.getByTestId('right-icon')).toBeInTheDocument()
  })

  it('applies full width style when isFullWidth is true', () => {
    renderWithTheme(<Button isFullWidth>Click me</Button>)
    expect(screen.getByRole('button')).toHaveStyle({ width: '100%' })
  })

  it('applies different sizes correctly', () => {
    const { rerender } = renderWithTheme(<Button size="sm">Small</Button>)
    expect(screen.getByRole('button')).toHaveStyle({ height: '2rem' })

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Button size="lg">Large</Button>
      </ThemeProvider>
    )
    expect(screen.getByRole('button')).toHaveStyle({ height: '3rem' })
  })

  it('applies different variants correctly', () => {
    const { rerender } = renderWithTheme(<Button variant="outline">Outline</Button>)
    expect(screen.getByRole('button')).toHaveStyle({ backgroundColor: 'transparent' })

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Button variant="ghost">Ghost</Button>
      </ThemeProvider>
    )
    expect(screen.getByRole('button')).toHaveStyle({ backgroundColor: 'transparent' })
  })

  it('is accessible using keyboard', () => {
    const handleClick = jest.fn()
    renderWithTheme(<Button onClick={handleClick}>Click me</Button>)
    
    const button = screen.getByRole('button')
    button.focus()
    expect(button).toHaveFocus()
    
    fireEvent.keyDown(button, { key: 'Enter' })
    expect(handleClick).toHaveBeenCalledTimes(1)
    
    fireEvent.keyDown(button, { key: ' ' })
    expect(handleClick).toHaveBeenCalledTimes(2)
  })
})

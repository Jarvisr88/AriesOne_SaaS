import React from 'react'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Tooltip } from './Tooltip'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Tooltip', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('renders trigger element', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Hover me</button>
      </Tooltip>
    )

    expect(screen.getByText('Hover me')).toBeInTheDocument()
  })

  it('shows tooltip on hover', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Hover me</button>
      </Tooltip>
    )

    fireEvent.mouseEnter(screen.getByText('Hover me'))
    act(() => {
      jest.advanceTimersByTime(200) // Default open delay
    })

    expect(screen.getByText('Tooltip content')).toBeInTheDocument()
  })

  it('hides tooltip on mouse leave', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Hover me</button>
      </Tooltip>
    )

    const trigger = screen.getByText('Hover me')
    
    fireEvent.mouseEnter(trigger)
    act(() => {
      jest.advanceTimersByTime(200)
    })
    
    fireEvent.mouseLeave(trigger)
    act(() => {
      jest.advanceTimersByTime(0) // Default close delay
    })

    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument()
  })

  it('respects open delay', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content" openDelay={500}>
        <button>Hover me</button>
      </Tooltip>
    )

    fireEvent.mouseEnter(screen.getByText('Hover me'))
    
    act(() => {
      jest.advanceTimersByTime(400)
    })
    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument()
    
    act(() => {
      jest.advanceTimersByTime(100)
    })
    expect(screen.getByText('Tooltip content')).toBeInTheDocument()
  })

  it('respects close delay', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content" closeDelay={500}>
        <button>Hover me</button>
      </Tooltip>
    )

    const trigger = screen.getByText('Hover me')
    
    fireEvent.mouseEnter(trigger)
    act(() => {
      jest.advanceTimersByTime(200)
    })
    
    fireEvent.mouseLeave(trigger)
    
    act(() => {
      jest.advanceTimersByTime(400)
    })
    expect(screen.getByText('Tooltip content')).toBeInTheDocument()
    
    act(() => {
      jest.advanceTimersByTime(100)
    })
    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument()
  })

  it('does not show tooltip when disabled', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content" isDisabled>
        <button>Hover me</button>
      </Tooltip>
    )

    fireEvent.mouseEnter(screen.getByText('Hover me'))
    act(() => {
      jest.advanceTimersByTime(200)
    })

    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument()
  })

  it('shows tooltip on click when trigger is click', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content" trigger="click">
        <button>Click me</button>
      </Tooltip>
    )

    fireEvent.click(screen.getByText('Click me'))
    act(() => {
      jest.advanceTimersByTime(200)
    })

    expect(screen.getByText('Tooltip content')).toBeInTheDocument()
  })

  it('toggles tooltip on click when trigger is click', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content" trigger="click">
        <button>Click me</button>
      </Tooltip>
    )

    const trigger = screen.getByText('Click me')
    
    fireEvent.click(trigger)
    act(() => {
      jest.advanceTimersByTime(200)
    })
    expect(screen.getByText('Tooltip content')).toBeInTheDocument()
    
    fireEvent.click(trigger)
    act(() => {
      jest.advanceTimersByTime(0)
    })
    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument()
  })

  it('calls onOpen when tooltip is shown', () => {
    const onOpen = jest.fn()
    renderWithTheme(
      <Tooltip content="Tooltip content" onOpen={onOpen}>
        <button>Hover me</button>
      </Tooltip>
    )

    fireEvent.mouseEnter(screen.getByText('Hover me'))
    act(() => {
      jest.advanceTimersByTime(200)
    })

    expect(onOpen).toHaveBeenCalled()
  })

  it('calls onClose when tooltip is hidden', () => {
    const onClose = jest.fn()
    renderWithTheme(
      <Tooltip content="Tooltip content" onClose={onClose}>
        <button>Hover me</button>
      </Tooltip>
    )

    const trigger = screen.getByText('Hover me')
    
    fireEvent.mouseEnter(trigger)
    act(() => {
      jest.advanceTimersByTime(200)
    })
    
    fireEvent.mouseLeave(trigger)
    act(() => {
      jest.advanceTimersByTime(0)
    })

    expect(onClose).toHaveBeenCalled()
  })

  it('handles controlled visibility', () => {
    const { rerender } = renderWithTheme(
      <Tooltip content="Tooltip content" isOpen={true}>
        <button>Hover me</button>
      </Tooltip>
    )

    expect(screen.getByText('Tooltip content')).toBeInTheDocument()

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Tooltip content="Tooltip content" isOpen={false}>
          <button>Hover me</button>
        </Tooltip>
      </ThemeProvider>
    )

    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument()
  })

  it('closes on escape key press', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Hover me</button>
      </Tooltip>
    )

    const trigger = screen.getByText('Hover me')
    
    fireEvent.mouseEnter(trigger)
    act(() => {
      jest.advanceTimersByTime(200)
    })
    
    fireEvent.keyDown(trigger, { key: 'Escape' })
    act(() => {
      jest.advanceTimersByTime(0)
    })

    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument()
  })

  it('adds correct ARIA attributes', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Hover me</button>
      </Tooltip>
    )

    const trigger = screen.getByText('Hover me')
    
    fireEvent.mouseEnter(trigger)
    act(() => {
      jest.advanceTimersByTime(200)
    })

    expect(trigger).toHaveAttribute('aria-describedby', 'tooltip')
    expect(screen.getByRole('tooltip')).toBeInTheDocument()
  })
})

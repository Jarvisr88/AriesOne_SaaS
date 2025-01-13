import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Popover } from './Popover'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Popover', () => {
  const mockOnClose = jest.fn()
  const mockOnOpen = jest.fn()
  const mockOnClosed = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders trigger element', () => {
    renderWithTheme(
      <Popover
        isOpen={false}
        onClose={mockOnClose}
        trigger={<button>Open Popover</button>}
      >
        Popover content
      </Popover>
    )

    expect(screen.getByText('Open Popover')).toBeInTheDocument()
  })

  it('shows popover when isOpen is true', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        trigger={<button>Open Popover</button>}
      >
        Popover content
      </Popover>
    )

    expect(screen.getByText('Popover content')).toBeInTheDocument()
  })

  it('renders header and footer when provided', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        trigger={<button>Open Popover</button>}
        header="Popover Header"
        footer={<button>Footer Button</button>}
      >
        Popover content
      </Popover>
    )

    expect(screen.getByText('Popover Header')).toBeInTheDocument()
    expect(screen.getByText('Footer Button')).toBeInTheDocument()
  })

  it('calls onClose when clicking close button', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        trigger={<button>Open Popover</button>}
      >
        Popover content
      </Popover>
    )

    fireEvent.click(screen.getByLabelText('Close popover'))
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('calls onClose when clicking outside if closeOnBlur is true', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        closeOnBlur={true}
        trigger={<button>Open Popover</button>}
      >
        Popover content
      </Popover>
    )

    fireEvent.mouseDown(document.body)
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('does not call onClose when clicking outside if closeOnBlur is false', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        closeOnBlur={false}
        trigger={<button>Open Popover</button>}
      >
        Popover content
      </Popover>
    )

    fireEvent.mouseDown(document.body)
    expect(mockOnClose).not.toHaveBeenCalled()
  })

  it('calls onClose when pressing escape if closeOnEsc is true', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        closeOnEsc={true}
        trigger={<button>Open Popover</button>}
      >
        Popover content
      </Popover>
    )

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('does not call onClose when pressing escape if closeOnEsc is false', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        closeOnEsc={false}
        trigger={<button>Open Popover</button>}
      >
        Popover content
      </Popover>
    )

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(mockOnClose).not.toHaveBeenCalled()
  })

  it('calls onOpen when popover opens', () => {
    const { rerender } = renderWithTheme(
      <Popover
        isOpen={false}
        onClose={mockOnClose}
        onOpen={mockOnOpen}
        trigger={<button>Open Popover</button>}
      >
        Popover content
      </Popover>
    )

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Popover
          isOpen={true}
          onClose={mockOnClose}
          onOpen={mockOnOpen}
          trigger={<button>Open Popover</button>}
        >
          Popover content
        </Popover>
      </ThemeProvider>
    )

    expect(mockOnOpen).toHaveBeenCalled()
  })

  it('calls onClosed when popover closes', () => {
    const { rerender } = renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        onClosed={mockOnClosed}
        trigger={<button>Open Popover</button>}
      >
        Popover content
      </Popover>
    )

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Popover
          isOpen={false}
          onClose={mockOnClose}
          onClosed={mockOnClosed}
          trigger={<button>Open Popover</button>}
        >
          Popover content
        </Popover>
      </ThemeProvider>
    )

    expect(mockOnClosed).toHaveBeenCalled()
  })

  it('hides close button when hideCloseButton is true', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        hideCloseButton={true}
        trigger={<button>Open Popover</button>}
      >
        Popover content
      </Popover>
    )

    expect(screen.queryByLabelText('Close popover')).not.toBeInTheDocument()
  })

  it('adds correct ARIA attributes to trigger', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        trigger={<button>Open Popover</button>}
        id="test-popover"
      >
        Popover content
      </Popover>
    )

    const trigger = screen.getByText('Open Popover')
    expect(trigger).toHaveAttribute('aria-expanded', 'true')
    expect(trigger).toHaveAttribute('aria-controls', 'test-popover')
    expect(trigger).toHaveAttribute('aria-haspopup', 'true')
  })

  it('adds correct ARIA attributes to popover', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        trigger={<button>Open Popover</button>}
        id="test-popover"
      >
        Popover content
      </Popover>
    )

    const popover = screen.getByRole('dialog')
    expect(popover).toHaveAttribute('aria-modal', 'true')
    expect(popover).toHaveAttribute('id', 'test-popover')
  })

  it('traps focus within the popover', () => {
    renderWithTheme(
      <Popover
        isOpen={true}
        onClose={mockOnClose}
        trigger={<button>Open Popover</button>}
      >
        <button>Button 1</button>
        <button>Button 2</button>
      </Popover>
    )

    const closeButton = screen.getByLabelText('Close popover')
    const button1 = screen.getByText('Button 1')
    const button2 = screen.getByText('Button 2')

    expect(document.activeElement).toBe(closeButton)

    button1.focus()
    expect(document.activeElement).toBe(button1)

    button2.focus()
    expect(document.activeElement).toBe(button2)
  })
})

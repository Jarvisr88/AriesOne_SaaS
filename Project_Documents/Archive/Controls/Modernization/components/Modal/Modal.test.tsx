import React from 'react'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Modal, ModalHeader, ModalBody, ModalFooter } from './Modal'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Modal', () => {
  const mockOnClose = jest.fn()
  const mockOnOpen = jest.fn()
  const mockOnClosed = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders when isOpen is true', () => {
    renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} id="test-modal">
        <ModalHeader>Test Modal</ModalHeader>
        <ModalBody>Modal content</ModalBody>
        <ModalFooter>
          <button>Close</button>
        </ModalFooter>
      </Modal>
    )

    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Test Modal')).toBeInTheDocument()
    expect(screen.getByText('Modal content')).toBeInTheDocument()
  })

  it('does not render when isOpen is false', () => {
    renderWithTheme(
      <Modal isOpen={false} onClose={mockOnClose} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('calls onClose when clicking the close button', () => {
    renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    fireEvent.click(screen.getByLabelText('Close modal'))
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('calls onClose when clicking the overlay if closeOnOverlayClick is true', () => {
    renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} closeOnOverlayClick={true} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    fireEvent.click(screen.getByRole('dialog'))
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('does not call onClose when clicking the overlay if closeOnOverlayClick is false', () => {
    renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} closeOnOverlayClick={false} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    fireEvent.click(screen.getByRole('dialog'))
    expect(mockOnClose).not.toHaveBeenCalled()
  })

  it('calls onClose when pressing escape if closeOnEsc is true', () => {
    renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} closeOnEsc={true} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('does not call onClose when pressing escape if closeOnEsc is false', () => {
    renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} closeOnEsc={false} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(mockOnClose).not.toHaveBeenCalled()
  })

  it('blocks scroll when blockScroll is true', () => {
    renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} blockScroll={true} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    expect(document.body.style.overflow).toBe('hidden')
  })

  it('does not block scroll when blockScroll is false', () => {
    renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} blockScroll={false} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    expect(document.body.style.overflow).not.toBe('hidden')
  })

  it('calls onOpen when modal opens', () => {
    const { rerender } = renderWithTheme(
      <Modal isOpen={false} onClose={mockOnClose} onOpen={mockOnOpen} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Modal isOpen={true} onClose={mockOnClose} onOpen={mockOnOpen} id="test-modal">
          <ModalBody>Modal content</ModalBody>
        </Modal>
      </ThemeProvider>
    )

    expect(mockOnOpen).toHaveBeenCalled()
  })

  it('calls onClosed when modal closes', () => {
    const { rerender } = renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} onClosed={mockOnClosed} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Modal isOpen={false} onClose={mockOnClose} onClosed={mockOnClosed} id="test-modal">
          <ModalBody>Modal content</ModalBody>
        </Modal>
      </ThemeProvider>
    )

    expect(mockOnClosed).toHaveBeenCalled()
  })

  it('applies correct size styles', () => {
    const { rerender } = renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} size="sm" id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    expect(screen.getByRole('dialog').firstChild).toHaveStyle({
      maxWidth: '480px'
    })

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Modal isOpen={true} onClose={mockOnClose} size="lg" id="test-modal">
          <ModalBody>Modal content</ModalBody>
        </Modal>
      </ThemeProvider>
    )

    expect(screen.getByRole('dialog').firstChild).toHaveStyle({
      maxWidth: '800px'
    })
  })

  it('hides close button when hideCloseButton is true', () => {
    renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} hideCloseButton={true} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    expect(screen.queryByLabelText('Close modal')).not.toBeInTheDocument()
  })

  it('traps focus within the modal', () => {
    renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} id="test-modal">
        <ModalHeader>Test Modal</ModalHeader>
        <ModalBody>
          <button>Button 1</button>
          <button>Button 2</button>
        </ModalBody>
        <ModalFooter>
          <button>Close</button>
        </ModalFooter>
      </Modal>
    )

    const closeButton = screen.getByLabelText('Close modal')
    const button1 = screen.getByText('Button 1')
    const button2 = screen.getByText('Button 2')
    const closeFooterButton = screen.getByText('Close')

    // Initial focus should be on the first focusable element
    expect(document.activeElement).toBe(closeButton)

    // Tab forward
    act(() => {
      button1.focus()
    })
    expect(document.activeElement).toBe(button1)

    act(() => {
      button2.focus()
    })
    expect(document.activeElement).toBe(button2)

    act(() => {
      closeFooterButton.focus()
    })
    expect(document.activeElement).toBe(closeFooterButton)
  })

  it('restores focus when closed', () => {
    const triggerButton = document.createElement('button')
    triggerButton.textContent = 'Open Modal'
    document.body.appendChild(triggerButton)
    triggerButton.focus()

    const { rerender } = renderWithTheme(
      <Modal isOpen={true} onClose={mockOnClose} id="test-modal">
        <ModalBody>Modal content</ModalBody>
      </Modal>
    )

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Modal isOpen={false} onClose={mockOnClose} id="test-modal">
          <ModalBody>Modal content</ModalBody>
        </Modal>
      </ThemeProvider>
    )

    expect(document.activeElement).toBe(triggerButton)
    document.body.removeChild(triggerButton)
  })
})

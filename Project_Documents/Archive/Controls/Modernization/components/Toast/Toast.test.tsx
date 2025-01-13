import React from 'react'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { ToastProvider, useToast } from './Toast'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

const TestComponent = () => {
  const toast = useToast()
  return (
    <div>
      <button onClick={() => toast.addToast({ title: 'Test Toast' })}>
        Show Toast
      </button>
      <button onClick={() => toast.removeAll()}>Remove All</button>
    </div>
  )
}

describe('Toast', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
  })

  it('shows toast when addToast is called', () => {
    renderWithTheme(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    fireEvent.click(screen.getByText('Show Toast'))
    expect(screen.getByText('Test Toast')).toBeInTheDocument()
  })

  it('removes toast after duration', () => {
    renderWithTheme(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    fireEvent.click(screen.getByText('Show Toast'))
    expect(screen.getByText('Test Toast')).toBeInTheDocument()

    act(() => {
      jest.advanceTimersByTime(5000) // Default duration
    })

    expect(screen.queryByText('Test Toast')).not.toBeInTheDocument()
  })

  it('removes toast when close button is clicked', () => {
    renderWithTheme(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    fireEvent.click(screen.getByText('Show Toast'))
    fireEvent.click(screen.getByLabelText('Close toast'))

    expect(screen.queryByText('Test Toast')).not.toBeInTheDocument()
  })

  it('removes all toasts when removeAll is called', () => {
    renderWithTheme(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    fireEvent.click(screen.getByText('Show Toast'))
    fireEvent.click(screen.getByText('Show Toast'))
    fireEvent.click(screen.getByText('Remove All'))

    expect(screen.queryAllByText('Test Toast')).toHaveLength(0)
  })

  it('limits number of toasts based on maxToasts prop', () => {
    renderWithTheme(
      <ToastProvider maxToasts={2}>
        <TestComponent />
      </ToastProvider>
    )

    fireEvent.click(screen.getByText('Show Toast'))
    fireEvent.click(screen.getByText('Show Toast'))
    fireEvent.click(screen.getByText('Show Toast'))

    expect(screen.queryAllByText('Test Toast')).toHaveLength(2)
  })

  it('renders toast with different statuses', () => {
    const TestStatusComponent = () => {
      const toast = useToast()
      return (
        <div>
          <button
            onClick={() =>
              toast.addToast({
                title: 'Success Toast',
                status: 'success'
              })
            }
          >
            Show Success
          </button>
          <button
            onClick={() =>
              toast.addToast({
                title: 'Error Toast',
                status: 'error'
              })
            }
          >
            Show Error
          </button>
        </div>
      )
    }

    renderWithTheme(
      <ToastProvider>
        <TestStatusComponent />
      </ToastProvider>
    )

    fireEvent.click(screen.getByText('Show Success'))
    expect(screen.getByText('Success Toast')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Show Error'))
    expect(screen.getByText('Error Toast')).toBeInTheDocument()
  })

  it('renders toast with title and description', () => {
    const TestDescriptionComponent = () => {
      const toast = useToast()
      return (
        <button
          onClick={() =>
            toast.addToast({
              title: 'Toast Title',
              description: 'Toast Description'
            })
          }
        >
          Show Toast
        </button>
      )
    }

    renderWithTheme(
      <ToastProvider>
        <TestDescriptionComponent />
      </ToastProvider>
    )

    fireEvent.click(screen.getByText('Show Toast'))
    expect(screen.getByText('Toast Title')).toBeInTheDocument()
    expect(screen.getByText('Toast Description')).toBeInTheDocument()
  })

  it('does not show close button when isClosable is false', () => {
    const TestClosableComponent = () => {
      const toast = useToast()
      return (
        <button
          onClick={() =>
            toast.addToast({
              title: 'Toast Title',
              isClosable: false
            })
          }
        >
          Show Toast
        </button>
      )
    }

    renderWithTheme(
      <ToastProvider>
        <TestClosableComponent />
      </ToastProvider>
    )

    fireEvent.click(screen.getByText('Show Toast'))
    expect(screen.queryByLabelText('Close toast')).not.toBeInTheDocument()
  })

  it('maintains toast with infinite duration', () => {
    const TestInfiniteComponent = () => {
      const toast = useToast()
      return (
        <button
          onClick={() =>
            toast.addToast({
              title: 'Infinite Toast',
              duration: Infinity
            })
          }
        >
          Show Toast
        </button>
      )
    }

    renderWithTheme(
      <ToastProvider>
        <TestInfiniteComponent />
      </ToastProvider>
    )

    fireEvent.click(screen.getByText('Show Toast'))
    
    act(() => {
      jest.advanceTimersByTime(10000)
    })

    expect(screen.getByText('Infinite Toast')).toBeInTheDocument()
  })

  it('adds correct ARIA attributes', () => {
    renderWithTheme(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    fireEvent.click(screen.getByText('Show Toast'))

    expect(screen.getByRole('region')).toHaveAttribute('aria-live', 'polite')
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })
})

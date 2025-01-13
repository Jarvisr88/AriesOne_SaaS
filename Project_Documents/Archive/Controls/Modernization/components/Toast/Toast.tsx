import React, { createContext, useContext, useCallback, useState } from 'react'
import { createPortal } from 'react-dom'
import styled, { css, keyframes } from 'styled-components'
import { Theme } from '../../theme/theme'

export type ToastPosition = 'top' | 'top-right' | 'top-left' | 'bottom' | 'bottom-right' | 'bottom-left'
export type ToastStatus = 'info' | 'success' | 'warning' | 'error'

export interface Toast {
  id: string
  title?: string
  description?: string
  status?: ToastStatus
  duration?: number
  isClosable?: boolean
}

interface ToastContextValue {
  addToast: (toast: Omit<Toast, 'id'>) => string
  removeToast: (id: string) => void
  removeAll: () => void
}

const ToastContext = createContext<ToastContextValue>({
  addToast: () => '',
  removeToast: () => {},
  removeAll: () => {}
})

export interface ToastProviderProps {
  children: React.ReactNode
  position?: ToastPosition
  maxToasts?: number
}

const slideIn = {
  top: keyframes`
    from { transform: translateY(-100%); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  `,
  'top-right': keyframes`
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  `,
  'top-left': keyframes`
    from { transform: translateX(-100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  `,
  bottom: keyframes`
    from { transform: translateY(100%); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  `,
  'bottom-right': keyframes`
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  `,
  'bottom-left': keyframes`
    from { transform: translateX(-100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  `
}

const getPositionStyles = (position: ToastPosition) => {
  const positions = {
    'top': css`
      top: ${props => props.theme.spacing.md};
      left: 50%;
      transform: translateX(-50%);
    `,
    'top-right': css`
      top: ${props => props.theme.spacing.md};
      right: ${props => props.theme.spacing.md};
    `,
    'top-left': css`
      top: ${props => props.theme.spacing.md};
      left: ${props => props.theme.spacing.md};
    `,
    'bottom': css`
      bottom: ${props => props.theme.spacing.md};
      left: 50%;
      transform: translateX(-50%);
    `,
    'bottom-right': css`
      bottom: ${props => props.theme.spacing.md};
      right: ${props => props.theme.spacing.md};
    `,
    'bottom-left': css`
      bottom: ${props => props.theme.spacing.md};
      left: ${props => props.theme.spacing.md};
    `
  }

  return positions[position]
}

const ToastContainer = styled.div<{ position: ToastPosition }>`
  position: fixed;
  z-index: 5000;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
  max-width: 560px;
  width: calc(100% - ${props => props.theme.spacing.lg});

  ${props => getPositionStyles(props.position)}
`

const statusColors = {
  info: css`
    background-color: ${props => props.theme.colors.primary[500]};
    color: ${props => props.theme.colors.white};
  `,
  success: css`
    background-color: ${props => props.theme.colors.success[500]};
    color: ${props => props.theme.colors.white};
  `,
  warning: css`
    background-color: ${props => props.theme.colors.warning[500]};
    color: ${props => props.theme.colors.neutral[900]};
  `,
  error: css`
    background-color: ${props => props.theme.colors.error[500]};
    color: ${props => props.theme.colors.white};
  `
}

const ToastElement = styled.div<{
  status: ToastStatus
  position: ToastPosition
}>`
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.radii.md};
  box-shadow: ${props => props.theme.shadows.lg};
  animation: ${props => slideIn[props.position]} 0.3s ease-out;

  ${props => statusColors[props.status]}
`

const ToastContent = styled.div`
  flex: 1;
  min-width: 0;
`

const ToastTitle = styled.div`
  font-weight: ${props => props.theme.fontWeights.medium};
  margin-bottom: ${props => props.theme.spacing.xs};
`

const ToastDescription = styled.div`
  font-size: ${props => props.theme.fontSizes.sm};
`

const CloseButton = styled.button`
  background: none;
  border: none;
  padding: ${props => props.theme.spacing.xs};
  margin: -${props => props.theme.spacing.xs};
  color: currentColor;
  opacity: 0.7;
  cursor: pointer;
  transition: opacity 0.2s;

  &:hover {
    opacity: 1;
  }

  &:focus-visible {
    outline: 2px solid currentColor;
    outline-offset: 2px;
  }
`

export const ToastProvider: React.FC<ToastProviderProps> = ({
  children,
  position = 'bottom-right',
  maxToasts = 3
}) => {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = useCallback(
    (toast: Omit<Toast, 'id'>) => {
      const id = Math.random().toString(36).substr(2, 9)
      const newToast: Toast = {
        id,
        status: 'info',
        duration: 5000,
        isClosable: true,
        ...toast
      }

      setToasts(currentToasts => {
        const updatedToasts = [newToast, ...currentToasts].slice(0, maxToasts)
        return updatedToasts
      })

      if (newToast.duration !== Infinity) {
        setTimeout(() => {
          removeToast(id)
        }, newToast.duration)
      }

      return id
    },
    [maxToasts]
  )

  const removeToast = useCallback((id: string) => {
    setToasts(currentToasts => currentToasts.filter(toast => toast.id !== id))
  }, [])

  const removeAll = useCallback(() => {
    setToasts([])
  }, [])

  return (
    <ToastContext.Provider value={{ addToast, removeToast, removeAll }}>
      {children}
      {createPortal(
        <ToastContainer
          role="region"
          aria-live="polite"
          position={position}
        >
          {toasts.map(toast => (
            <ToastElement
              key={toast.id}
              status={toast.status || 'info'}
              position={position}
              role="alert"
            >
              <ToastContent>
                {toast.title && <ToastTitle>{toast.title}</ToastTitle>}
                {toast.description && (
                  <ToastDescription>{toast.description}</ToastDescription>
                )}
              </ToastContent>
              {toast.isClosable && (
                <CloseButton
                  onClick={() => removeToast(toast.id)}
                  aria-label="Close toast"
                >
                  ✕
                </CloseButton>
              )}
            </ToastElement>
          ))}
        </ToastContainer>,
        document.body
      )}
    </ToastContext.Provider>
  )
}

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

ToastProvider.displayName = 'ToastProvider'

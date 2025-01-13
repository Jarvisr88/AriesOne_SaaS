import React, { useEffect, useRef, useCallback, createContext, useContext } from 'react'
import { createPortal } from 'react-dom'
import styled, { css, keyframes } from 'styled-components'
import { Theme } from '../../theme/theme'
import { FocusScope } from '@react-aria/focus'

export type ModalSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full'

interface ModalContextValue {
  onClose: () => void
}

const ModalContext = createContext<ModalContextValue>({
  onClose: () => {}
})

export interface ModalProps {
  /** If true, the modal will be open */
  isOpen: boolean
  /** Called when the modal should close */
  onClose: () => void
  /** The size of the modal */
  size?: ModalSize
  /** If true, the modal will close when clicking outside or pressing escape */
  closeOnOverlayClick?: boolean
  /** If true, the modal will close when pressing escape */
  closeOnEsc?: boolean
  /** If true, scrolling will be blocked while the modal is open */
  blockScroll?: boolean
  /** If true, the close button will be hidden */
  hideCloseButton?: boolean
  /** The z-index of the modal */
  zIndex?: number
  /** The children of the modal */
  children: React.ReactNode
  /** Called when the modal has opened */
  onOpen?: () => void
  /** Called when the modal has closed */
  onClosed?: () => void
  /** The id of the modal */
  id?: string
}

const fadeIn = keyframes`
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
`

const slideIn = keyframes`
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
`

const sizeStyles = {
  xs: css`
    max-width: 320px;
  `,
  sm: css`
    max-width: 480px;
  `,
  md: css`
    max-width: 640px;
  `,
  lg: css`
    max-width: 800px;
  `,
  xl: css`
    max-width: 960px;
  `,
  full: css`
    max-width: 100%;
    height: 100%;
    margin: 0;
    border-radius: 0;
  `
}

const Overlay = styled.div<{ zIndex?: number }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: ${props => props.zIndex || 1000};
  animation: ${fadeIn} 0.2s ease-out;
`

const ModalContainer = styled.div<{ size?: ModalSize }>`
  position: relative;
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.size === 'full' ? 0 : props.theme.radii.lg};
  box-shadow: ${props => props.theme.shadows.xl};
  width: 100%;
  margin: ${props => props.theme.spacing.md};
  animation: ${slideIn} 0.3s ease-out;
  
  ${props => sizeStyles[props.size || 'md']}
`

const CloseButton = styled.button`
  position: absolute;
  top: ${props => props.theme.spacing.md};
  right: ${props => props.theme.spacing.md};
  width: 2rem;
  height: 2rem;
  padding: 0;
  background: none;
  border: none;
  border-radius: ${props => props.theme.radii.md};
  cursor: pointer;
  color: ${props => props.theme.colors.neutral[500]};
  transition: ${props => props.theme.transitions.default};

  &:hover {
    background-color: ${props => props.theme.colors.neutral[100]};
    color: ${props => props.theme.colors.neutral[700]};
  }

  &:focus-visible {
    outline: none;
    box-shadow: 0 0 0 2px ${props => props.theme.colors.primary[500]};
  }

  &::before,
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 25%;
    width: 50%;
    height: 2px;
    background-color: currentColor;
  }

  &::before {
    transform: rotate(45deg);
  }

  &::after {
    transform: rotate(-45deg);
  }
`

export const ModalHeader = styled.header`
  padding: ${props => props.theme.spacing.lg};
  padding-right: ${props => props.theme.spacing.xl};
  border-bottom: 1px solid ${props => props.theme.colors.neutral[200]};
`

export const ModalBody = styled.div`
  padding: ${props => props.theme.spacing.lg};
  overflow-y: auto;
  max-height: calc(100vh - 200px);

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.neutral[100]};
  }

  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.neutral[300]};
    border-radius: 4px;
  }
`

export const ModalFooter = styled.footer`
  padding: ${props => props.theme.spacing.lg};
  border-top: 1px solid ${props => props.theme.colors.neutral[200]};
  display: flex;
  justify-content: flex-end;
  gap: ${props => props.theme.spacing.sm};
`

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  size = 'md',
  closeOnOverlayClick = true,
  closeOnEsc = true,
  blockScroll = true,
  hideCloseButton = false,
  zIndex,
  children,
  onOpen,
  onClosed,
  id
}) => {
  const overlayRef = useRef<HTMLDivElement>(null)
  const modalRef = useRef<HTMLDivElement>(null)
  const previousActiveElement = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement
      onOpen?.()
    } else {
      previousActiveElement.current?.focus()
      onClosed?.()
    }
  }, [isOpen, onOpen, onClosed])

  useEffect(() => {
    if (blockScroll) {
      if (isOpen) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }

    return () => {
      if (blockScroll) {
        document.body.style.overflow = ''
      }
    }
  }, [isOpen, blockScroll])

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === 'Escape' && closeOnEsc) {
        onClose()
      }
    },
    [onClose, closeOnEsc]
  )

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, handleKeyDown])

  const handleOverlayClick = useCallback(
    (event: React.MouseEvent) => {
      if (
        closeOnOverlayClick &&
        event.target === overlayRef.current &&
        !modalRef.current?.contains(event.target as Node)
      ) {
        onClose()
      }
    },
    [onClose, closeOnOverlayClick]
  )

  if (!isOpen) return null

  return createPortal(
    <ModalContext.Provider value={{ onClose }}>
      <Overlay
        ref={overlayRef}
        onClick={handleOverlayClick}
        zIndex={zIndex}
        role="dialog"
        aria-modal="true"
        aria-labelledby={`${id}-title`}
        aria-describedby={`${id}-description`}
      >
        <FocusScope contain restoreFocus autoFocus>
          <ModalContainer
            ref={modalRef}
            size={size}
          >
            {!hideCloseButton && (
              <CloseButton
                onClick={onClose}
                aria-label="Close modal"
              />
            )}
            {children}
          </ModalContainer>
        </FocusScope>
      </Overlay>
    </ModalContext.Provider>,
    document.body
  )
}

export const useModal = () => {
  const context = useContext(ModalContext)
  if (!context) {
    throw new Error('useModal must be used within a Modal')
  }
  return context
}

Modal.displayName = 'Modal'

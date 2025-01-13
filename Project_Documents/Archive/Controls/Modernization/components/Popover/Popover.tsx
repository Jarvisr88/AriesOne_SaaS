import React, { useState, useRef, useCallback, useEffect } from 'react'
import { createPortal } from 'react-dom'
import styled, { css, keyframes } from 'styled-components'
import { Theme } from '../../theme/theme'
import { FocusScope } from '@react-aria/focus'

export type PopoverPlacement = 
  | 'top'
  | 'top-start'
  | 'top-end'
  | 'bottom'
  | 'bottom-start'
  | 'bottom-end'
  | 'left'
  | 'left-start'
  | 'left-end'
  | 'right'
  | 'right-start'
  | 'right-end'

export interface PopoverProps {
  /** If true, the popover will be shown */
  isOpen: boolean
  /** Called when the popover should close */
  onClose: () => void
  /** The placement of the popover */
  placement?: PopoverPlacement
  /** The header content */
  header?: React.ReactNode
  /** The body content */
  children: React.ReactNode
  /** The footer content */
  footer?: React.ReactNode
  /** If true, the close button will be hidden */
  hideCloseButton?: boolean
  /** If true, clicking outside will close the popover */
  closeOnBlur?: boolean
  /** If true, pressing escape will close the popover */
  closeOnEsc?: boolean
  /** The trigger element */
  trigger: React.ReactElement
  /** The z-index of the popover */
  zIndex?: number
  /** The width of the popover */
  width?: string
  /** The offset from the trigger element */
  offset?: number
  /** Called when the popover has opened */
  onOpen?: () => void
  /** Called when the popover has closed */
  onClosed?: () => void
  /** The id of the popover */
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

const getPlacementStyles = (placement: PopoverPlacement, offset: number) => {
  const placements = {
    'top': css`
      bottom: 100%;
      left: 50%;
      transform: translateX(-50%) translateY(-${offset}px);
    `,
    'top-start': css`
      bottom: 100%;
      left: 0;
      transform: translateY(-${offset}px);
    `,
    'top-end': css`
      bottom: 100%;
      right: 0;
      transform: translateY(-${offset}px);
    `,
    'bottom': css`
      top: 100%;
      left: 50%;
      transform: translateX(-50%) translateY(${offset}px);
    `,
    'bottom-start': css`
      top: 100%;
      left: 0;
      transform: translateY(${offset}px);
    `,
    'bottom-end': css`
      top: 100%;
      right: 0;
      transform: translateY(${offset}px);
    `,
    'left': css`
      right: 100%;
      top: 50%;
      transform: translateY(-50%) translateX(-${offset}px);
    `,
    'left-start': css`
      right: 100%;
      top: 0;
      transform: translateX(-${offset}px);
    `,
    'left-end': css`
      right: 100%;
      bottom: 0;
      transform: translateX(-${offset}px);
    `,
    'right': css`
      left: 100%;
      top: 50%;
      transform: translateY(-50%) translateX(${offset}px);
    `,
    'right-start': css`
      left: 100%;
      top: 0;
      transform: translateX(${offset}px);
    `,
    'right-end': css`
      left: 100%;
      bottom: 0;
      transform: translateX(${offset}px);
    `
  }

  return placements[placement]
}

const getArrowStyles = (placement: PopoverPlacement) => {
  const arrowPlacements = {
    'top': css`
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%) rotate(45deg);
    `,
    'top-start': css`
      bottom: -8px;
      left: 24px;
      transform: rotate(45deg);
    `,
    'top-end': css`
      bottom: -8px;
      right: 24px;
      transform: rotate(45deg);
    `,
    'bottom': css`
      top: -8px;
      left: 50%;
      transform: translateX(-50%) rotate(45deg);
    `,
    'bottom-start': css`
      top: -8px;
      left: 24px;
      transform: rotate(45deg);
    `,
    'bottom-end': css`
      top: -8px;
      right: 24px;
      transform: rotate(45deg);
    `,
    'left': css`
      right: -8px;
      top: 50%;
      transform: translateY(-50%) rotate(45deg);
    `,
    'left-start': css`
      right: -8px;
      top: 24px;
      transform: rotate(45deg);
    `,
    'left-end': css`
      right: -8px;
      bottom: 24px;
      transform: rotate(45deg);
    `,
    'right': css`
      left: -8px;
      top: 50%;
      transform: translateY(-50%) rotate(45deg);
    `,
    'right-start': css`
      left: -8px;
      top: 24px;
      transform: rotate(45deg);
    `,
    'right-end': css`
      left: -8px;
      bottom: 24px;
      transform: rotate(45deg);
    `
  }

  return arrowPlacements[placement]
}

const PopoverTrigger = styled.div`
  display: inline-block;
  position: relative;
`

const PopoverContainer = styled.div<{
  placement: PopoverPlacement
  offset: number
  width?: string
  zIndex?: number
}>`
  position: absolute;
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.radii.md};
  box-shadow: ${props => props.theme.shadows.lg};
  width: ${props => props.width || '300px'};
  z-index: ${props => props.zIndex || 1000};
  animation: ${fadeIn} 0.2s ease-out;

  ${props => getPlacementStyles(props.placement, props.offset)}
`

const Arrow = styled.div<{ placement: PopoverPlacement }>`
  position: absolute;
  width: 16px;
  height: 16px;
  background-color: ${props => props.theme.colors.white};
  box-shadow: ${props => props.theme.shadows.lg};
  
  ${props => getArrowStyles(props.placement)}
`

const CloseButton = styled.button`
  position: absolute;
  top: ${props => props.theme.spacing.sm};
  right: ${props => props.theme.spacing.sm};
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

const PopoverHeader = styled.header`
  padding: ${props => props.theme.spacing.md};
  border-bottom: 1px solid ${props => props.theme.colors.neutral[200]};
  font-weight: ${props => props.theme.fontWeights.medium};
`

const PopoverBody = styled.div`
  padding: ${props => props.theme.spacing.md};
`

const PopoverFooter = styled.footer`
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.neutral[200]};
  display: flex;
  justify-content: flex-end;
  gap: ${props => props.theme.spacing.sm};
`

export const Popover: React.FC<PopoverProps> = ({
  isOpen,
  onClose,
  placement = 'bottom',
  header,
  children,
  footer,
  hideCloseButton = false,
  closeOnBlur = true,
  closeOnEsc = true,
  trigger,
  zIndex,
  width,
  offset = 8,
  onOpen,
  onClosed,
  id
}) => {
  const triggerRef = useRef<HTMLDivElement>(null)
  const popoverRef = useRef<HTMLDivElement>(null)
  const [uniqueId] = useState(() => id || `popover-${Math.random().toString(36).substr(2, 9)}`)

  useEffect(() => {
    if (isOpen) {
      onOpen?.()
    } else {
      onClosed?.()
    }
  }, [isOpen, onOpen, onClosed])

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

  const handleClickOutside = useCallback(
    (event: MouseEvent) => {
      if (
        closeOnBlur &&
        popoverRef.current &&
        triggerRef.current &&
        !popoverRef.current.contains(event.target as Node) &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        onClose()
      }
    },
    [onClose, closeOnBlur]
  )

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen, handleClickOutside])

  const clonedTrigger = React.cloneElement(trigger, {
    'aria-expanded': isOpen,
    'aria-controls': uniqueId,
    'aria-haspopup': true
  })

  return (
    <PopoverTrigger ref={triggerRef}>
      {clonedTrigger}
      {isOpen &&
        createPortal(
          <FocusScope contain restoreFocus autoFocus>
            <PopoverContainer
              ref={popoverRef}
              id={uniqueId}
              role="dialog"
              aria-modal="true"
              placement={placement}
              offset={offset}
              width={width}
              zIndex={zIndex}
            >
              {!hideCloseButton && (
                <CloseButton
                  onClick={onClose}
                  aria-label="Close popover"
                />
              )}
              {header && <PopoverHeader>{header}</PopoverHeader>}
              <PopoverBody>{children}</PopoverBody>
              {footer && <PopoverFooter>{footer}</PopoverFooter>}
              <Arrow placement={placement} />
            </PopoverContainer>
          </FocusScope>,
          document.body
        )}
    </PopoverTrigger>
  )
}

Popover.displayName = 'Popover'

import React, { useState, useRef, useCallback, useEffect } from 'react'
import { createPortal } from 'react-dom'
import styled, { css, keyframes } from 'styled-components'
import { Theme } from '../../theme/theme'

export type TooltipPlacement = 
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

export interface TooltipProps {
  /** The content to show in the tooltip */
  content: React.ReactNode
  /** The placement of the tooltip */
  placement?: TooltipPlacement
  /** If true, the tooltip will be shown */
  isOpen?: boolean
  /** The delay before showing the tooltip (ms) */
  openDelay?: number
  /** The delay before hiding the tooltip (ms) */
  closeDelay?: number
  /** If true, the tooltip will be disabled */
  isDisabled?: boolean
  /** The z-index of the tooltip */
  zIndex?: number
  /** The max width of the tooltip */
  maxWidth?: string
  /** If true, the tooltip will wrap to multiple lines */
  shouldWrap?: boolean
  /** The children that will trigger the tooltip */
  children: React.ReactElement
  /** The offset from the reference element */
  offset?: number
  /** If true, the tooltip will be shown on click instead of hover */
  trigger?: 'hover' | 'click'
  /** Called when the tooltip is shown */
  onOpen?: () => void
  /** Called when the tooltip is hidden */
  onClose?: () => void
}

const fadeIn = keyframes`
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
`

const getPlacementStyles = (placement: TooltipPlacement, offset: number) => {
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

const getArrowStyles = (placement: TooltipPlacement) => {
  const arrowPlacements = {
    'top': css`
      bottom: -4px;
      left: 50%;
      transform: translateX(-50%) rotate(45deg);
    `,
    'top-start': css`
      bottom: -4px;
      left: 12px;
      transform: rotate(45deg);
    `,
    'top-end': css`
      bottom: -4px;
      right: 12px;
      transform: rotate(45deg);
    `,
    'bottom': css`
      top: -4px;
      left: 50%;
      transform: translateX(-50%) rotate(45deg);
    `,
    'bottom-start': css`
      top: -4px;
      left: 12px;
      transform: rotate(45deg);
    `,
    'bottom-end': css`
      top: -4px;
      right: 12px;
      transform: rotate(45deg);
    `,
    'left': css`
      right: -4px;
      top: 50%;
      transform: translateY(-50%) rotate(45deg);
    `,
    'left-start': css`
      right: -4px;
      top: 12px;
      transform: rotate(45deg);
    `,
    'left-end': css`
      right: -4px;
      bottom: 12px;
      transform: rotate(45deg);
    `,
    'right': css`
      left: -4px;
      top: 50%;
      transform: translateY(-50%) rotate(45deg);
    `,
    'right-start': css`
      left: -4px;
      top: 12px;
      transform: rotate(45deg);
    `,
    'right-end': css`
      left: -4px;
      bottom: 12px;
      transform: rotate(45deg);
    `
  }

  return arrowPlacements[placement]
}

const TooltipContainer = styled.div<{
  placement: TooltipPlacement
  offset: number
  maxWidth?: string
  shouldWrap?: boolean
  zIndex?: number
}>`
  position: absolute;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  background-color: ${props => props.theme.colors.neutral[800]};
  color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.radii.sm};
  font-size: ${props => props.theme.fontSizes.sm};
  line-height: 1.4;
  white-space: ${props => props.shouldWrap ? 'normal' : 'nowrap'};
  max-width: ${props => props.maxWidth || 'none'};
  pointer-events: none;
  z-index: ${props => props.zIndex || 1000};
  animation: ${fadeIn} 0.2s ease-out;

  ${props => getPlacementStyles(props.placement, props.offset)}
`

const Arrow = styled.div<{ placement: TooltipPlacement }>`
  position: absolute;
  width: 8px;
  height: 8px;
  background-color: ${props => props.theme.colors.neutral[800]};
  
  ${props => getArrowStyles(props.placement)}
`

const TooltipTrigger = styled.div`
  display: inline-block;
  position: relative;
`

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  placement = 'top',
  isOpen: controlledIsOpen,
  openDelay = 200,
  closeDelay = 0,
  isDisabled = false,
  zIndex,
  maxWidth,
  shouldWrap = false,
  children,
  offset = 8,
  trigger = 'hover',
  onOpen,
  onClose
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const triggerRef = useRef<HTMLDivElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)
  const openTimeoutRef = useRef<NodeJS.Timeout>()
  const closeTimeoutRef = useRef<NodeJS.Timeout>()

  const showTooltip = useCallback(() => {
    if (isDisabled) return

    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
    }

    openTimeoutRef.current = setTimeout(() => {
      setIsOpen(true)
      onOpen?.()
    }, openDelay)
  }, [isDisabled, openDelay, onOpen])

  const hideTooltip = useCallback(() => {
    if (openTimeoutRef.current) {
      clearTimeout(openTimeoutRef.current)
    }

    closeTimeoutRef.current = setTimeout(() => {
      setIsOpen(false)
      onClose?.()
    }, closeDelay)
  }, [closeDelay, onClose])

  const toggleTooltip = useCallback(() => {
    if (isOpen) {
      hideTooltip()
    } else {
      showTooltip()
    }
  }, [isOpen, showTooltip, hideTooltip])

  useEffect(() => {
    return () => {
      if (openTimeoutRef.current) clearTimeout(openTimeoutRef.current)
      if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current)
    }
  }, [])

  useEffect(() => {
    if (controlledIsOpen !== undefined) {
      setIsOpen(controlledIsOpen)
    }
  }, [controlledIsOpen])

  const handleMouseEnter = () => {
    if (trigger === 'hover') showTooltip()
  }

  const handleMouseLeave = () => {
    if (trigger === 'hover') hideTooltip()
  }

  const handleClick = () => {
    if (trigger === 'click') toggleTooltip()
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape' && isOpen) {
      hideTooltip()
    }
  }

  const clonedChild = React.cloneElement(children, {
    onMouseEnter: handleMouseEnter,
    onMouseLeave: handleMouseLeave,
    onClick: handleClick,
    onKeyDown: handleKeyDown,
    'aria-describedby': isOpen ? 'tooltip' : undefined
  })

  return (
    <TooltipTrigger ref={triggerRef}>
      {clonedChild}
      {isOpen &&
        createPortal(
          <TooltipContainer
            ref={tooltipRef}
            id="tooltip"
            role="tooltip"
            placement={placement}
            offset={offset}
            maxWidth={maxWidth}
            shouldWrap={shouldWrap}
            zIndex={zIndex}
          >
            {content}
            <Arrow placement={placement} />
          </TooltipContainer>,
          document.body
        )}
    </TooltipTrigger>
  )
}

Tooltip.displayName = 'Tooltip'

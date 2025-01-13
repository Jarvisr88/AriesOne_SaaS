import React, { createContext, useContext, useCallback, useState, useRef, useEffect } from 'react'
import styled, { css, keyframes } from 'styled-components'
import { createPortal } from 'react-dom'
import { FocusScope } from '@react-aria/focus'

export type MenuPlacement = 'bottom' | 'bottom-start' | 'bottom-end' | 'right' | 'right-start' | 'right-end'

interface MenuContextValue {
  isOpen: boolean
  onClose: () => void
  menuId: string
}

const MenuContext = createContext<MenuContextValue>({
  isOpen: false,
  onClose: () => {},
  menuId: ''
})

export interface MenuProps {
  children: React.ReactNode
  isOpen?: boolean
  onClose?: () => void
  placement?: MenuPlacement
  offset?: number
  id?: string
}

export interface MenuButtonProps {
  children: React.ReactNode
}

export interface MenuListProps {
  children: React.ReactNode
}

export interface MenuItemProps {
  children: React.ReactNode
  icon?: React.ReactElement
  command?: string
  isDisabled?: boolean
  onClick?: () => void
}

export interface MenuDividerProps {
  className?: string
}

export interface MenuGroupProps {
  children: React.ReactNode
  title?: string
}

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideIn = {
  bottom: keyframes`
    from { transform: translateY(-10px); }
    to { transform: translateY(0); }
  `,
  'bottom-start': keyframes`
    from { transform: translateY(-10px); }
    to { transform: translateY(0); }
  `,
  'bottom-end': keyframes`
    from { transform: translateY(-10px); }
    to { transform: translateY(0); }
  `,
  right: keyframes`
    from { transform: translateX(-10px); }
    to { transform: translateX(0); }
  `,
  'right-start': keyframes`
    from { transform: translateX(-10px); }
    to { transform: translateX(0); }
  `,
  'right-end': keyframes`
    from { transform: translateX(-10px); }
    to { transform: translateX(0); }
  `
}

const getPlacementStyles = (placement: MenuPlacement, offset: number) => {
  const placements = {
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
    'right': css`
      top: 50%;
      left: 100%;
      transform: translateY(-50%) translateX(${offset}px);
    `,
    'right-start': css`
      top: 0;
      left: 100%;
      transform: translateX(${offset}px);
    `,
    'right-end': css`
      bottom: 0;
      left: 100%;
      transform: translateX(${offset}px);
    `
  }

  return placements[placement]
}

const MenuButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.neutral[300]};
  border-radius: ${props => props.theme.radii.md};
  background-color: ${props => props.theme.colors.white};
  color: ${props => props.theme.colors.neutral[900]};
  font-size: ${props => props.theme.fontSizes.md};
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background-color: ${props => props.theme.colors.neutral[50]};
  }

  &:focus-visible {
    outline: none;
    box-shadow: 0 0 0 2px ${props => props.theme.colors.primary[500]};
  }

  &[aria-expanded="true"] {
    background-color: ${props => props.theme.colors.neutral[100]};
  }
`

const MenuListContainer = styled.div<{
  placement: MenuPlacement
  offset: number
}>`
  position: absolute;
  z-index: 1000;
  min-width: 200px;
  padding: ${props => props.theme.spacing.xs} 0;
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.radii.md};
  box-shadow: ${props => props.theme.shadows.lg};
  animation: ${fadeIn} 0.2s ease-out,
             ${props => slideIn[props.placement]} 0.2s ease-out;

  ${props => getPlacementStyles(props.placement, props.offset)}
`

const StyledMenuItem = styled.button<{ isDisabled?: boolean }>`
  display: flex;
  align-items: center;
  width: 100%;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: none;
  background: none;
  color: ${props =>
    props.isDisabled
      ? props.theme.colors.neutral[400]
      : props.theme.colors.neutral[900]};
  font-size: ${props => props.theme.fontSizes.md};
  text-align: left;
  cursor: ${props => (props.isDisabled ? 'not-allowed' : 'pointer')};
  transition: background-color 0.2s;

  &:hover:not(:disabled) {
    background-color: ${props => props.theme.colors.neutral[100]};
  }

  &:focus-visible {
    outline: none;
    background-color: ${props => props.theme.colors.neutral[100]};
  }

  &:disabled {
    pointer-events: none;
  }
`

const MenuItemIcon = styled.span`
  display: inline-flex;
  margin-right: ${props => props.theme.spacing.sm};
  color: ${props => props.theme.colors.neutral[500]};
`

const MenuItemCommand = styled.span`
  margin-left: auto;
  padding-left: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.neutral[500]};
  font-size: ${props => props.theme.fontSizes.sm};
`

const MenuDivider = styled.hr`
  margin: ${props => props.theme.spacing.xs} 0;
  border: none;
  border-top: 1px solid ${props => props.theme.colors.neutral[200]};
`

const MenuGroupTitle = styled.div`
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.neutral[500]};
  font-size: ${props => props.theme.fontSizes.sm};
  font-weight: ${props => props.theme.fontWeights.medium};
`

export const Menu: React.FC<MenuProps> = ({
  children,
  isOpen = false,
  onClose,
  placement = 'bottom',
  offset = 8,
  id
}) => {
  const menuId = useRef(id || `menu-${Math.random().toString(36).substr(2, 9)}`)
  const [uniqueId] = useState(menuId.current)

  return (
    <MenuContext.Provider
      value={{
        isOpen,
        onClose: onClose || (() => {}),
        menuId: uniqueId
      }}
    >
      {children}
    </MenuContext.Provider>
  )
}

export const MenuTrigger: React.FC<MenuButtonProps> = ({ children }) => {
  const { isOpen, menuId } = useContext(MenuContext)
  const triggerRef = useRef<HTMLDivElement>(null)

  return (
    <div ref={triggerRef}>
      {React.cloneElement(React.Children.only(children) as React.ReactElement, {
        'aria-haspopup': 'menu',
        'aria-expanded': isOpen,
        'aria-controls': menuId
      })}
    </div>
  )
}

export const MenuList: React.FC<MenuListProps> = ({ children }) => {
  const { isOpen, onClose, menuId } = useContext(MenuContext)
  const menuRef = useRef<HTMLDivElement>(null)

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    },
    [onClose]
  )

  const handleClickOutside = useCallback(
    (event: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node)
      ) {
        onClose()
      }
    },
    [onClose]
  )

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen, handleKeyDown, handleClickOutside])

  if (!isOpen) return null

  return createPortal(
    <FocusScope contain restoreFocus autoFocus>
      <MenuListContainer
        ref={menuRef}
        role="menu"
        id={menuId}
        placement="bottom"
        offset={8}
      >
        {children}
      </MenuListContainer>
    </FocusScope>,
    document.body
  )
}

export const MenuItem: React.FC<MenuItemProps> = ({
  children,
  icon,
  command,
  isDisabled,
  onClick
}) => {
  const { onClose } = useContext(MenuContext)

  const handleClick = () => {
    if (!isDisabled) {
      onClick?.()
      onClose()
    }
  }

  return (
    <StyledMenuItem
      role="menuitem"
      onClick={handleClick}
      isDisabled={isDisabled}
      disabled={isDisabled}
      tabIndex={isDisabled ? -1 : 0}
    >
      {icon && <MenuItemIcon>{icon}</MenuItemIcon>}
      {children}
      {command && <MenuItemCommand>{command}</MenuItemCommand>}
    </StyledMenuItem>
  )
}

export const MenuDividerComponent: React.FC<MenuDividerProps> = ({ className }) => (
  <MenuDivider role="separator" className={className} />
)

export const MenuGroup: React.FC<MenuGroupProps> = ({ children, title }) => (
  <div role="group" aria-label={title}>
    {title && <MenuGroupTitle>{title}</MenuGroupTitle>}
    {children}
  </div>
)

Menu.displayName = 'Menu'
MenuTrigger.displayName = 'MenuTrigger'
MenuList.displayName = 'MenuList'
MenuItem.displayName = 'MenuItem'
MenuDividerComponent.displayName = 'MenuDivider'
MenuGroup.displayName = 'MenuGroup'

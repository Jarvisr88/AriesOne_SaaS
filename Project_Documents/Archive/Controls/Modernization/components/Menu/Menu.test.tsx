import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Menu, MenuTrigger, MenuList, MenuItem, MenuGroup, MenuDividerComponent } from './Menu'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Menu', () => {
  const onClose = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders menu button', () => {
    renderWithTheme(
      <Menu>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem>Item 1</MenuItem>
        </MenuList>
      </Menu>
    )

    expect(screen.getByText('Open Menu')).toBeInTheDocument()
  })

  it('shows menu list when isOpen is true', () => {
    renderWithTheme(
      <Menu isOpen>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem>Item 1</MenuItem>
        </MenuList>
      </Menu>
    )

    expect(screen.getByText('Item 1')).toBeInTheDocument()
  })

  it('hides menu list when isOpen is false', () => {
    renderWithTheme(
      <Menu isOpen={false}>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem>Item 1</MenuItem>
        </MenuList>
      </Menu>
    )

    expect(screen.queryByText('Item 1')).not.toBeInTheDocument()
  })

  it('calls onClose when clicking outside', () => {
    renderWithTheme(
      <Menu isOpen onClose={onClose}>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem>Item 1</MenuItem>
        </MenuList>
      </Menu>
    )

    fireEvent.mouseDown(document.body)
    expect(onClose).toHaveBeenCalled()
  })

  it('calls onClose when pressing escape', () => {
    renderWithTheme(
      <Menu isOpen onClose={onClose}>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem>Item 1</MenuItem>
        </MenuList>
      </Menu>
    )

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onClose).toHaveBeenCalled()
  })

  it('calls onClick when menu item is clicked', () => {
    const onClick = jest.fn()
    renderWithTheme(
      <Menu isOpen onClose={onClose}>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem onClick={onClick}>Item 1</MenuItem>
        </MenuList>
      </Menu>
    )

    fireEvent.click(screen.getByText('Item 1'))
    expect(onClick).toHaveBeenCalled()
    expect(onClose).toHaveBeenCalled()
  })

  it('does not call onClick when disabled menu item is clicked', () => {
    const onClick = jest.fn()
    renderWithTheme(
      <Menu isOpen onClose={onClose}>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem onClick={onClick} isDisabled>
            Item 1
          </MenuItem>
        </MenuList>
      </Menu>
    )

    fireEvent.click(screen.getByText('Item 1'))
    expect(onClick).not.toHaveBeenCalled()
    expect(onClose).not.toHaveBeenCalled()
  })

  it('renders menu item with icon and command', () => {
    renderWithTheme(
      <Menu isOpen>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem
            icon={<span data-testid="icon">✓</span>}
            command="Ctrl+S"
          >
            Item 1
          </MenuItem>
        </MenuList>
      </Menu>
    )

    expect(screen.getByTestId('icon')).toBeInTheDocument()
    expect(screen.getByText('Ctrl+S')).toBeInTheDocument()
  })

  it('renders menu group with title', () => {
    renderWithTheme(
      <Menu isOpen>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuGroup title="Group 1">
            <MenuItem>Item 1</MenuItem>
          </MenuGroup>
        </MenuList>
      </Menu>
    )

    expect(screen.getByText('Group 1')).toBeInTheDocument()
  })

  it('renders menu divider', () => {
    renderWithTheme(
      <Menu isOpen>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem>Item 1</MenuItem>
          <MenuDividerComponent />
          <MenuItem>Item 2</MenuItem>
        </MenuList>
      </Menu>
    )

    expect(screen.getByRole('separator')).toBeInTheDocument()
  })

  it('adds correct ARIA attributes to trigger', () => {
    renderWithTheme(
      <Menu isOpen>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem>Item 1</MenuItem>
        </MenuList>
      </Menu>
    )

    const trigger = screen.getByText('Open Menu')
    expect(trigger).toHaveAttribute('aria-haspopup', 'menu')
    expect(trigger).toHaveAttribute('aria-expanded', 'true')
    expect(trigger).toHaveAttribute('aria-controls')
  })

  it('adds correct ARIA attributes to menu items', () => {
    renderWithTheme(
      <Menu isOpen>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuItem>Item 1</MenuItem>
          <MenuItem isDisabled>Item 2</MenuItem>
        </MenuList>
      </Menu>
    )

    const item1 = screen.getByText('Item 1')
    const item2 = screen.getByText('Item 2')

    expect(item1).toHaveAttribute('role', 'menuitem')
    expect(item1).toHaveAttribute('tabIndex', '0')
    expect(item2).toHaveAttribute('role', 'menuitem')
    expect(item2).toHaveAttribute('tabIndex', '-1')
    expect(item2).toBeDisabled()
  })

  it('adds correct ARIA attributes to menu group', () => {
    renderWithTheme(
      <Menu isOpen>
        <MenuTrigger>
          <button>Open Menu</button>
        </MenuTrigger>
        <MenuList>
          <MenuGroup title="Group 1">
            <MenuItem>Item 1</MenuItem>
          </MenuGroup>
        </MenuList>
      </Menu>
    )

    const group = screen.getByRole('group')
    expect(group).toHaveAttribute('aria-label', 'Group 1')
  })
})

import React from 'react'
import { render, screen, fireEvent, within } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { Table } from './Table'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Table', () => {
  const mockData = [
    { id: 1, name: 'John Doe', age: 30 },
    { id: 2, name: 'Jane Smith', age: 25 },
    { id: 3, name: 'Bob Johnson', age: 35 }
  ]

  const columns = [
    { Header: 'ID', accessor: 'id' },
    { Header: 'Name', accessor: 'name' },
    { Header: 'Age', accessor: 'age' }
  ]

  it('renders table with data', () => {
    renderWithTheme(
      <Table
        data={mockData}
        columns={columns}
      />
    )

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
    expect(screen.getByText('Bob Johnson')).toBeInTheDocument()
  })

  it('shows empty message when no data', () => {
    const emptyMessage = 'No data available'
    renderWithTheme(
      <Table
        data={[]}
        columns={columns}
        emptyMessage={emptyMessage}
      />
    )

    expect(screen.getByText(emptyMessage)).toBeInTheDocument()
  })

  it('shows error message when error occurs', () => {
    const errorMessage = 'Failed to load data'
    renderWithTheme(
      <Table
        data={[]}
        columns={columns}
        error={errorMessage}
      />
    )

    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('enables row selection when selectable is true', () => {
    const onSelectionChange = jest.fn()
    renderWithTheme(
      <Table
        data={mockData}
        columns={columns}
        selectable
        onSelectionChange={onSelectionChange}
      />
    )

    const checkboxes = screen.getAllByRole('checkbox')
    expect(checkboxes).toHaveLength(mockData.length + 1) // +1 for header checkbox

    fireEvent.click(checkboxes[1]) // Click first row checkbox
    expect(onSelectionChange).toHaveBeenCalled()
  })

  it('enables sorting when sortable is true', () => {
    const onSortChange = jest.fn()
    renderWithTheme(
      <Table
        data={mockData}
        columns={columns}
        sortable
        onSortChange={onSortChange}
      />
    )

    const nameHeader = screen.getByText('Name')
    fireEvent.click(nameHeader)
    expect(onSortChange).toHaveBeenCalled()
  })

  it('shows pagination when enabled', () => {
    renderWithTheme(
      <Table
        data={mockData}
        columns={columns}
        paginate
        pageSize={2}
      />
    )

    expect(screen.getByText('Page 1 of 2')).toBeInTheDocument()
    expect(screen.getByText('Next')).toBeInTheDocument()
    expect(screen.getByText('Previous')).toBeInTheDocument()
  })

  it('handles page navigation', () => {
    const onPageChange = jest.fn()
    renderWithTheme(
      <Table
        data={mockData}
        columns={columns}
        paginate
        pageSize={2}
        onPageChange={onPageChange}
      />
    )

    const nextButton = screen.getByText('Next')
    fireEvent.click(nextButton)
    expect(onPageChange).toHaveBeenCalledWith(1)
  })

  it('shows loading state', () => {
    renderWithTheme(
      <Table
        data={mockData}
        columns={columns}
        loading
      />
    )

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('applies custom styles via className', () => {
    const customClass = 'custom-table'
    renderWithTheme(
      <Table
        data={mockData}
        columns={columns}
        className={customClass}
      />
    )

    const tableContainer = screen.getByRole('table').parentElement
    expect(tableContainer).toHaveClass(customClass)
  })

  it('handles keyboard navigation', () => {
    renderWithTheme(
      <Table
        data={mockData}
        columns={columns}
        selectable
      />
    )

    const checkboxes = screen.getAllByRole('checkbox')
    checkboxes[1].focus()
    fireEvent.keyDown(checkboxes[1], { key: 'Space' })
    expect(checkboxes[1]).toBeChecked()
  })

  it('maintains accessibility attributes', () => {
    renderWithTheme(
      <Table
        data={mockData}
        columns={columns}
      />
    )

    const table = screen.getByRole('table')
    expect(table).toBeInTheDocument()
    expect(table).toHaveAttribute('role', 'table')
  })
})

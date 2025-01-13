import React, { useState, useCallback, useMemo } from 'react'
import styled, { css } from 'styled-components'
import { useTable, useRowSelect, useSortBy, usePagination, Column } from 'react-table'

export interface TableProps<T extends object> {
  /** Data to display in the table */
  data: T[]
  /** Column definitions */
  columns: Column<T>[]
  /** Enable row selection */
  selectable?: boolean
  /** Enable sorting */
  sortable?: boolean
  /** Enable pagination */
  paginate?: boolean
  /** Items per page when pagination is enabled */
  pageSize?: number
  /** Loading state */
  loading?: boolean
  /** Error state */
  error?: Error | string
  /** Empty state message */
  emptyMessage?: string
  /** Callback when row selection changes */
  onSelectionChange?: (selectedRows: T[]) => void
  /** Callback when sort changes */
  onSortChange?: (sortBy: { id: string; desc: boolean }[]) => void
  /** Callback when page changes */
  onPageChange?: (page: number) => void
  /** Additional CSS class */
  className?: string
}

const TableContainer = styled.div`
  width: 100%;
  overflow-x: auto;
  border: 1px solid ${props => props.theme.colors.neutral[200]};
  border-radius: ${props => props.theme.radii.md};
`

const StyledTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  font-size: ${props => props.theme.fontSizes.sm};
`

const TableHead = styled.thead`
  background-color: ${props => props.theme.colors.neutral[50]};
  border-bottom: 1px solid ${props => props.theme.colors.neutral[200]};
`

const TableBody = styled.tbody`
  background-color: ${props => props.theme.colors.white};
`

const TableRow = styled.tr<{ selected?: boolean }>`
  &:hover {
    background-color: ${props => props.theme.colors.neutral[50]};
  }

  ${props =>
    props.selected &&
    css`
      background-color: ${props.theme.colors.primary[50]};
      &:hover {
        background-color: ${props.theme.colors.primary[100]};
      }
    `}
`

const TableCell = styled.td`
  padding: ${props => props.theme.spacing.md};
  border-bottom: 1px solid ${props => props.theme.colors.neutral[200]};
  color: ${props => props.theme.colors.neutral[900]};
`

const TableHeaderCell = styled.th<{ sortable?: boolean }>`
  padding: ${props => props.theme.spacing.md};
  text-align: left;
  font-weight: ${props => props.theme.fontWeights.medium};
  color: ${props => props.theme.colors.neutral[700]};
  user-select: none;

  ${props =>
    props.sortable &&
    css`
      cursor: pointer;
      &:hover {
        background-color: ${props.theme.colors.neutral[100]};
      }
    `}
`

const SortIcon = styled.span<{ ascending?: boolean }>`
  display: inline-block;
  margin-left: ${props => props.theme.spacing.xs};
  transition: transform 0.2s;
  
  ${props =>
    props.ascending &&
    css`
      transform: rotate(180deg);
    `}
`

const Pagination = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.neutral[200]};
  background-color: ${props => props.theme.colors.white};
`

const PaginationButton = styled.button<{ disabled?: boolean }>`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.neutral[300]};
  border-radius: ${props => props.theme.radii.sm};
  background-color: ${props => props.theme.colors.white};
  color: ${props => props.theme.colors.neutral[700]};
  cursor: pointer;

  &:hover:not(:disabled) {
    background-color: ${props => props.theme.colors.neutral[50]};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.8);
`

const ErrorMessage = styled.div`
  padding: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.error[500]};
  text-align: center;
`

const EmptyMessage = styled.div`
  padding: ${props => props.theme.spacing.xl};
  text-align: center;
  color: ${props => props.theme.colors.neutral[500]};
`

export function Table<T extends object>({
  data,
  columns,
  selectable = false,
  sortable = false,
  paginate = false,
  pageSize = 10,
  loading = false,
  error,
  emptyMessage = 'No data available',
  onSelectionChange,
  onSortChange,
  onPageChange,
  className
}: TableProps<T>) {
  const [selectedRowIds, setSelectedRowIds] = useState<Record<string, boolean>>({})

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
    gotoPage,
    canPreviousPage,
    canNextPage,
    pageCount,
    nextPage,
    previousPage,
    state: { pageIndex, sortBy, selectedRowIds: selectedRows }
  } = useTable(
    {
      columns,
      data,
      initialState: { pageSize },
    },
    useSortBy,
    usePagination,
    useRowSelect,
    hooks => {
      if (selectable) {
        hooks.visibleColumns.push(columns => [
          {
            id: 'selection',
            Header: ({ getToggleAllRowsSelectedProps }) => (
              <input type="checkbox" {...getToggleAllRowsSelectedProps()} />
            ),
            Cell: ({ row }) => (
              <input type="checkbox" {...row.getToggleRowSelectedProps()} />
            )
          },
          ...columns
        ])
      }
    }
  )

  const handleSelectionChange = useCallback(() => {
    if (onSelectionChange) {
      const selectedRows = Object.keys(selectedRowIds).map(id => data[parseInt(id)])
      onSelectionChange(selectedRows)
    }
  }, [selectedRowIds, data, onSelectionChange])

  const handleSortChange = useCallback(() => {
    if (onSortChange) {
      onSortChange(sortBy)
    }
  }, [sortBy, onSortChange])

  const handlePageChange = useCallback((newPage: number) => {
    gotoPage(newPage)
    if (onPageChange) {
      onPageChange(newPage)
    }
  }, [gotoPage, onPageChange])

  // Memoize the table content
  const tableContent = useMemo(() => {
    if (error) {
      return (
        <ErrorMessage>
          {typeof error === 'string' ? error : error.message}
        </ErrorMessage>
      )
    }

    if (!loading && (!data || data.length === 0)) {
      return <EmptyMessage>{emptyMessage}</EmptyMessage>
    }

    return (
      <TableBody {...getTableBodyProps()}>
        {page.map(row => {
          prepareRow(row)
          return (
            <TableRow
              {...row.getRowProps()}
              selected={row.isSelected}
            >
              {row.cells.map(cell => (
                <TableCell {...cell.getCellProps()}>
                  {cell.render('Cell')}
                </TableCell>
              ))}
            </TableRow>
          )
        })}
      </TableBody>
    )
  }, [data, loading, error, emptyMessage, page, prepareRow, getTableBodyProps])

  return (
    <TableContainer className={className}>
      <StyledTable {...getTableProps()}>
        <TableHead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <TableHeaderCell
                  {...column.getHeaderProps(sortable ? column.getSortByToggleProps() : undefined)}
                  sortable={sortable && column.canSort}
                >
                  {column.render('Header')}
                  {sortable && column.isSorted && (
                    <SortIcon ascending={!column.isSortedDesc}>
                      ▼
                    </SortIcon>
                  )}
                </TableHeaderCell>
              ))}
            </tr>
          ))}
        </TableHead>
        {tableContent}
      </StyledTable>

      {loading && (
        <LoadingOverlay>
          Loading...
        </LoadingOverlay>
      )}

      {paginate && pageCount > 1 && (
        <Pagination>
          <div>
            Page {pageIndex + 1} of {pageCount}
          </div>
          <div>
            <PaginationButton
              onClick={() => handlePageChange(pageIndex - 1)}
              disabled={!canPreviousPage}
            >
              Previous
            </PaginationButton>
            <PaginationButton
              onClick={() => handlePageChange(pageIndex + 1)}
              disabled={!canNextPage}
            >
              Next
            </PaginationButton>
          </div>
        </Pagination>
      )}
    </TableContainer>
  )
}

Table.displayName = 'Table'

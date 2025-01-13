import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReportList } from '../ReportList';
import { useReports } from '../../hooks/useReports';

// Mock the custom hook
jest.mock('../../hooks/useReports');

describe('ReportList', () => {
  const mockReports = [
    {
      id: '1',
      name: 'Test Report 1',
      description: 'Description 1',
      category: { id: '1', name: 'Category 1' },
      createdBy: 'user1',
      updatedAt: new Date().toISOString(),
      isSystem: false,
    },
    {
      id: '2',
      name: 'Test Report 2',
      description: 'Description 2',
      category: { id: '1', name: 'Category 1' },
      createdBy: 'user2',
      updatedAt: new Date().toISOString(),
      isSystem: true,
    },
  ];

  const mockHook = {
    reports: mockReports,
    totalCount: 2,
    isLoading: false,
    error: null,
    deleteReports: jest.fn(),
    cloneReport: jest.fn(),
    exportReport: jest.fn(),
  };

  beforeEach(() => {
    (useReports as jest.Mock).mockReturnValue(mockHook);
  });

  it('renders report list', () => {
    render(<ReportList />);
    expect(screen.getByText('Test Report 1')).toBeInTheDocument();
    expect(screen.getByText('Test Report 2')).toBeInTheDocument();
  });

  it('handles search', async () => {
    render(<ReportList />);
    const searchInput = screen.getByPlaceholderText('Search reports...');
    
    await userEvent.type(searchInput, 'test');
    
    expect(useReports).toHaveBeenCalledWith(
      expect.objectContaining({
        searchText: 'test',
      }),
    );
  });

  it('handles report selection', () => {
    render(<ReportList />);
    const checkbox = screen.getAllByRole('checkbox')[1]; // First row checkbox
    
    fireEvent.click(checkbox);
    
    expect(checkbox).toBeChecked();
  });

  it('disables selection for system reports', () => {
    render(<ReportList />);
    const checkboxes = screen.getAllByRole('checkbox');
    const systemReportCheckbox = checkboxes[2]; // Second row checkbox
    
    expect(systemReportCheckbox).toBeDisabled();
  });

  it('handles bulk delete', async () => {
    render(<ReportList />);
    
    // Select first report
    const checkbox = screen.getAllByRole('checkbox')[1];
    fireEvent.click(checkbox);
    
    // Click delete button
    const deleteButton = screen.getByText(/Delete Selected/);
    fireEvent.click(deleteButton);
    
    expect(mockHook.deleteReports).toHaveBeenCalledWith(['1']);
  });

  it('handles report menu actions', async () => {
    render(<ReportList />);
    
    // Open menu for first report
    const menuButton = screen.getAllByTestId('more-menu')[0];
    fireEvent.click(menuButton);
    
    // Click clone option
    const cloneButton = screen.getByText('Clone');
    fireEvent.click(cloneButton);
    
    expect(mockHook.cloneReport).toHaveBeenCalledWith('1');
  });

  it('handles export actions', async () => {
    render(<ReportList />);
    
    // Open menu for first report
    const menuButton = screen.getAllByTestId('more-menu')[0];
    fireEvent.click(menuButton);
    
    // Click export options
    const exportPdfButton = screen.getByText('Export as PDF');
    fireEvent.click(exportPdfButton);
    
    expect(mockHook.exportReport).toHaveBeenCalledWith('1', 'pdf');
  });

  it('displays error state', () => {
    (useReports as jest.Mock).mockReturnValue({
      ...mockHook,
      error: new Error('Failed to load reports'),
    });
    
    render(<ReportList />);
    expect(screen.getByText(/Failed to load reports/)).toBeInTheDocument();
  });

  it('displays loading state', () => {
    (useReports as jest.Mock).mockReturnValue({
      ...mockHook,
      isLoading: true,
      reports: [],
    });
    
    render(<ReportList />);
    expect(screen.getByText(/Loading/)).toBeInTheDocument();
  });

  it('handles select all', () => {
    render(<ReportList />);
    
    // Click select all checkbox
    const selectAllCheckbox = screen.getAllByRole('checkbox')[0];
    fireEvent.click(selectAllCheckbox);
    
    // Verify all non-system reports are selected
    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes[1]).toBeChecked();
    expect(checkboxes[2]).not.toBeChecked(); // System report
  });
});

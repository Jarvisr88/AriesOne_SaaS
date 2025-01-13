import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import userEvent from '@testing-library/user-event';
import { toast } from '@/components/ui/use-toast';
import BulkUpdateInterface from '@/components/BulkUpdateInterface';

// Mock dependencies
jest.mock('@/components/ui/use-toast', () => ({
  toast: jest.fn(),
}));

// Mock XLSX
jest.mock('xlsx', () => ({
  read: jest.fn(),
  utils: {
    sheet_to_json: jest.fn(),
  },
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithProviders = (ui: React.ReactElement) => {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>
      {ui}
    </QueryClientProvider>
  );
};

describe('BulkUpdateInterface', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
  });

  it('renders file upload area', () => {
    renderWithProviders(<BulkUpdateInterface />);
    
    expect(screen.getByText(/drag and drop/i)).toBeInTheDocument();
    expect(screen.getByText(/supports xlsx, xls, and csv/i)).toBeInTheDocument();
  });

  it('handles file upload successfully', async () => {
    const mockData = [
      {
        itemId: 'TEST001',
        basePrice: '100.00',
        currency: 'USD',
      },
    ];

    // Mock XLSX reading
    const XLSX = require('xlsx');
    XLSX.read.mockReturnValue({
      SheetNames: ['Sheet1'],
      Sheets: {
        Sheet1: {},
      },
    });
    XLSX.utils.sheet_to_json.mockReturnValue(mockData);

    renderWithProviders(<BulkUpdateInterface />);
    
    // Create a mock file
    const file = new File(
      ['dummy content'],
      'test.xlsx',
      { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
    );

    // Simulate file drop
    const dropzone = screen.getByText(/drag and drop/i).parentElement!;
    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: [file],
      },
    });

    // Verify data is displayed
    await waitFor(() => {
      expect(screen.getByText('TEST001')).toBeInTheDocument();
      expect(screen.getByText('100.00')).toBeInTheDocument();
      expect(screen.getByText('USD')).toBeInTheDocument();
    });
  });

  it('handles bulk update submission', async () => {
    // Mock successful API response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        successful: 1,
        failed: 0,
      }),
    });

    const mockData = [
      {
        itemId: 'TEST001',
        basePrice: '100.00',
        currency: 'USD',
      },
    ];

    // Mock XLSX reading
    const XLSX = require('xlsx');
    XLSX.read.mockReturnValue({
      SheetNames: ['Sheet1'],
      Sheets: {
        Sheet1: {},
      },
    });
    XLSX.utils.sheet_to_json.mockReturnValue(mockData);

    renderWithProviders(<BulkUpdateInterface />);
    
    // Upload file
    const file = new File(
      ['dummy content'],
      'test.xlsx',
      { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
    );

    const dropzone = screen.getByText(/drag and drop/i).parentElement!;
    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: [file],
      },
    });

    // Wait for file processing
    await waitFor(() => {
      expect(screen.getByText(/process 1 updates/i)).toBeInTheDocument();
    });

    // Submit updates
    const submitButton = screen.getByText(/process 1 updates/i);
    fireEvent.click(submitButton);

    // Verify API call
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/prices/bulk-update',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: expect.any(String),
        })
      );
    });

    // Verify success toast
    expect(toast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Success',
        description: expect.stringContaining('Successfully processed 1 updates'),
      })
    );
  });

  it('handles file upload errors', async () => {
    // Mock XLSX error
    const XLSX = require('xlsx');
    XLSX.read.mockImplementation(() => {
      throw new Error('Invalid file format');
    });

    renderWithProviders(<BulkUpdateInterface />);
    
    // Upload invalid file
    const file = new File(
      ['invalid content'],
      'test.xlsx',
      { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
    );

    const dropzone = screen.getByText(/drag and drop/i).parentElement!;
    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: [file],
      },
    });

    // Verify error toast
    await waitFor(() => {
      expect(toast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Error',
          description: 'Failed to parse file',
          variant: 'destructive',
        })
      );
    });
  });

  it('handles bulk update errors', async () => {
    // Mock API error
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({
        message: 'Bulk update failed',
      }),
    });

    const mockData = [
      {
        itemId: 'TEST001',
        basePrice: '100.00',
        currency: 'USD',
      },
    ];

    // Mock XLSX reading
    const XLSX = require('xlsx');
    XLSX.read.mockReturnValue({
      SheetNames: ['Sheet1'],
      Sheets: {
        Sheet1: {},
      },
    });
    XLSX.utils.sheet_to_json.mockReturnValue(mockData);

    renderWithProviders(<BulkUpdateInterface />);
    
    // Upload file
    const file = new File(
      ['dummy content'],
      'test.xlsx',
      { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
    );

    const dropzone = screen.getByText(/drag and drop/i).parentElement!;
    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: [file],
      },
    });

    // Submit updates
    await waitFor(() => {
      const submitButton = screen.getByText(/process 1 updates/i);
      fireEvent.click(submitButton);
    });

    // Verify error toast
    await waitFor(() => {
      expect(toast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Error',
          description: 'Bulk update failed',
          variant: 'destructive',
        })
      );
    });
  });
});

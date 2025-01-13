import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import userEvent from '@testing-library/user-event';
import { toast } from '@/components/ui/use-toast';
import PriceEditor from '@/components/PriceEditor';

// Mock dependencies
jest.mock('@/components/ui/use-toast', () => ({
  toast: jest.fn(),
}));

// Create a new QueryClient for each test
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

// Wrapper component with providers
const renderWithProviders = (ui: React.ReactElement) => {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>
      {ui}
    </QueryClientProvider>
  );
};

describe('PriceEditor', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    
    // Mock fetch globally
    global.fetch = jest.fn();
  });

  it('renders all form fields', () => {
    renderWithProviders(<PriceEditor />);
    
    expect(screen.getByLabelText(/item id/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/base price/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/currency/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/effective date/i)).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    renderWithProviders(<PriceEditor />);
    
    // Try to submit without filling required fields
    const submitButton = screen.getByRole('button', { name: /update price/i });
    fireEvent.click(submitButton);
    
    // Check for validation messages
    await waitFor(() => {
      expect(screen.getByText(/item id is required/i)).toBeInTheDocument();
    });
  });

  it('successfully submits valid form data', async () => {
    // Mock successful API response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'success' }),
    });

    renderWithProviders(<PriceEditor />);
    
    // Fill out form
    await userEvent.type(screen.getByLabelText(/item id/i), 'TEST001');
    await userEvent.type(screen.getByLabelText(/base price/i), '100.00');
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: /update price/i });
    fireEvent.click(submitButton);
    
    // Verify API call
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/prices/update',
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
        description: expect.any(String),
      })
    );
  });

  it('handles API errors appropriately', async () => {
    // Mock API error response
    const errorMessage = 'Invalid price format';
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ message: errorMessage }),
    });

    renderWithProviders(<PriceEditor />);
    
    // Fill out form
    await userEvent.type(screen.getByLabelText(/item id/i), 'TEST001');
    await userEvent.type(screen.getByLabelText(/base price/i), 'invalid');
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: /update price/i });
    fireEvent.click(submitButton);
    
    // Verify error toast
    await waitFor(() => {
      expect(toast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Error',
          description: errorMessage,
          variant: 'destructive',
        })
      );
    });
  });

  it('disables submit button while processing', async () => {
    // Mock slow API response
    (global.fetch as jest.Mock).mockImplementationOnce(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderWithProviders(<PriceEditor />);
    
    // Fill out form
    await userEvent.type(screen.getByLabelText(/item id/i), 'TEST001');
    await userEvent.type(screen.getByLabelText(/base price/i), '100.00');
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: /update price/i });
    fireEvent.click(submitButton);
    
    // Verify button is disabled
    expect(submitButton).toBeDisabled();
    
    // Wait for submission to complete
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });

  it('resets form after successful submission', async () => {
    // Mock successful API response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'success' }),
    });

    renderWithProviders(<PriceEditor />);
    
    // Fill out form
    const itemIdInput = screen.getByLabelText(/item id/i);
    const basePriceInput = screen.getByLabelText(/base price/i);
    
    await userEvent.type(itemIdInput, 'TEST001');
    await userEvent.type(basePriceInput, '100.00');
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: /update price/i });
    fireEvent.click(submitButton);
    
    // Verify form reset
    await waitFor(() => {
      expect(itemIdInput).toHaveValue('');
      expect(basePriceInput).toHaveValue('');
    });
  });
});

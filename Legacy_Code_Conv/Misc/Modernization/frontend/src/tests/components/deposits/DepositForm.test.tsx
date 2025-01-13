/**
 * Deposit form component tests
 */
import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../../utils/test-utils';
import { DepositForm } from '../../../components/deposits/DepositForm';

describe('DepositForm', () => {
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    mockOnSuccess.mockClear();
  });

  it('renders deposit form with required fields', () => {
    render(<DepositForm onSuccess={mockOnSuccess} />);

    expect(screen.getByLabelText(/amount/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/payment method/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/customer id/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create deposit/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    render(<DepositForm onSuccess={mockOnSuccess} />);

    const submitButton = screen.getByRole('button', { name: /create deposit/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/amount is required/i)).toBeInTheDocument();
      expect(screen.getByText(/payment method is required/i)).toBeInTheDocument();
      expect(screen.getByText(/customer id is required/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    render(<DepositForm onSuccess={mockOnSuccess} />);

    const amountInput = screen.getByLabelText(/amount/i);
    const paymentMethodSelect = screen.getByLabelText(/payment method/i);
    const customerIdInput = screen.getByLabelText(/customer id/i);
    const submitButton = screen.getByRole('button', { name: /create deposit/i });

    await userEvent.type(amountInput, '100.00');
    await userEvent.selectOptions(paymentMethodSelect, 'cash');
    await userEvent.type(customerIdInput, '1');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toHaveAttribute('disabled');
      expect(mockOnSuccess).toHaveBeenCalledWith(expect.objectContaining({
        amount: 100,
        paymentMethod: 'cash',
        customerId: 1
      }));
    });
  });

  it('shows error message on failed submission', async () => {
    server.use(
      rest.post('/deposits', (req, res, ctx) =>
        res(ctx.status(400), ctx.json({ message: 'Invalid deposit amount' }))
      )
    );

    render(<DepositForm onSuccess={mockOnSuccess} />);

    const amountInput = screen.getByLabelText(/amount/i);
    const paymentMethodSelect = screen.getByLabelText(/payment method/i);
    const customerIdInput = screen.getByLabelText(/customer id/i);
    const submitButton = screen.getByRole('button', { name: /create deposit/i });

    await userEvent.type(amountInput, '0');
    await userEvent.selectOptions(paymentMethodSelect, 'cash');
    await userEvent.type(customerIdInput, '1');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid deposit amount/i)).toBeInTheDocument();
      expect(mockOnSuccess).not.toHaveBeenCalled();
    });
  });

  it('validates amount is greater than 0', async () => {
    render(<DepositForm onSuccess={mockOnSuccess} />);

    const amountInput = screen.getByLabelText(/amount/i);
    await userEvent.type(amountInput, '0');

    await waitFor(() => {
      expect(screen.getByText(/amount must be greater than 0/i)).toBeInTheDocument();
    });
  });
});

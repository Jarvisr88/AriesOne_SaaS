import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AddressControl } from '../../../components/address/AddressControl';
import type { Address } from '../../../types/address';

const mockAddress: Address = {
  address1: '123 Main St',
  city: 'Springfield',
  state: 'IL',
  zip_code: '62701',
};

describe('AddressControl', () => {
  it('renders all fields correctly', () => {
    render(<AddressControl id="test" value={mockAddress} />);
    
    expect(screen.getByLabelText(/address line 1/i)).toHaveValue('123 Main St');
    expect(screen.getByLabelText(/city/i)).toHaveValue('Springfield');
    expect(screen.getByLabelText(/state/i)).toHaveValue('IL');
    expect(screen.getByLabelText(/zip code/i)).toHaveValue('62701');
  });

  it('handles field changes', () => {
    const handleChange = jest.fn();
    render(<AddressControl id="test" value={mockAddress} onChange={handleChange} />);
    
    const address1Input = screen.getByLabelText(/address line 1/i);
    fireEvent.change(address1Input, { target: { value: '456 Oak St' } });
    
    expect(handleChange).toHaveBeenCalledWith({
      ...mockAddress,
      address1: '456 Oak St',
    });
  });

  it('validates required fields', async () => {
    render(<AddressControl id="test" />);
    
    // Try to validate empty form
    const validateButton = screen.getByText(/validate/i);
    fireEvent.click(validateButton);
    
    await waitFor(() => {
      expect(screen.getByText(/required/i)).toBeInTheDocument();
    });
  });

  it('validates address format', async () => {
    const handleValidate = jest.fn();
    render(
      <AddressControl
        id="test"
        value={{
          ...mockAddress,
          state: 'Invalid',
        }}
        onValidate={handleValidate}
      />
    );
    
    const validateButton = screen.getByText(/validate/i);
    fireEvent.click(validateButton);
    
    await waitFor(() => {
      expect(handleValidate).toHaveBeenCalledWith(false);
    });
  });

  it('integrates with map button', () => {
    render(<AddressControl id="test" value={mockAddress} />);
    
    const mapButton = screen.getByText(/map/i);
    expect(mapButton).toBeEnabled();
    
    // Without address, button should be disabled
    render(<AddressControl id="test" />);
    expect(screen.getByText(/map/i)).toBeDisabled();
  });

  it('tracks changes correctly', async () => {
    const { container } = render(<AddressControl id="test" value={mockAddress} />);
    
    const address1Input = screen.getByLabelText(/address line 1/i);
    fireEvent.change(address1Input, { target: { value: '456 Oak St' } });
    
    await waitFor(() => {
      expect(container.querySelector('.is-modified')).toBeInTheDocument();
    });
  });
});

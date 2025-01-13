import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { NameControl } from '../../../components/name/NameControl';
import type { Name } from '../../../types/name';

const mockName: Name = {
  courtesy: 'Dr.',
  first_name: 'John',
  middle_name: 'William',
  last_name: 'Doe',
  suffix: 'Jr.',
};

describe('NameControl', () => {
  it('renders all fields correctly', () => {
    render(<NameControl id="test" value={mockName} />);
    
    expect(screen.getByLabelText(/title/i)).toHaveValue('Dr.');
    expect(screen.getByLabelText(/first name/i)).toHaveValue('John');
    expect(screen.getByLabelText(/middle/i)).toHaveValue('William');
    expect(screen.getByLabelText(/last name/i)).toHaveValue('Doe');
    expect(screen.getByLabelText(/suffix/i)).toHaveValue('Jr.');
  });

  it('handles field changes', () => {
    const handleChange = jest.fn();
    render(<NameControl id="test" value={mockName} onChange={handleChange} />);
    
    const firstNameInput = screen.getByLabelText(/first name/i);
    fireEvent.change(firstNameInput, { target: { value: 'Jane' } });
    
    expect(handleChange).toHaveBeenCalledWith({
      ...mockName,
      first_name: 'Jane',
    });
  });

  it('validates required fields', async () => {
    render(<NameControl id="test" />);
    
    // Try to submit empty form
    const firstNameInput = screen.getByLabelText(/first name/i);
    fireEvent.blur(firstNameInput);
    
    await waitFor(() => {
      expect(screen.getByText(/required/i)).toBeInTheDocument();
    });
  });

  it('formats names correctly', async () => {
    render(<NameControl id="test" value={mockName} />);
    
    await waitFor(() => {
      expect(screen.getByText(/Dr. John William Doe Jr./i)).toBeInTheDocument();
      expect(screen.getByText(/Doe, Dr. John W. Jr./i)).toBeInTheDocument();
    });
  });

  it('handles courtesy title selection', () => {
    const handleChange = jest.fn();
    render(<NameControl id="test" value={mockName} onChange={handleChange} />);
    
    const titleSelect = screen.getByLabelText(/title/i);
    fireEvent.change(titleSelect, { target: { value: 'Mr.' } });
    
    expect(handleChange).toHaveBeenCalledWith({
      ...mockName,
      courtesy: 'Mr.',
    });
  });

  it('validates suffix format', async () => {
    render(<NameControl id="test" value={mockName} />);
    
    const suffixInput = screen.getByLabelText(/suffix/i);
    fireEvent.change(suffixInput, { target: { value: 'Invalid' } });
    
    await waitFor(() => {
      expect(screen.getByText(/invalid suffix/i)).toBeInTheDocument();
    });
  });

  it('tracks changes correctly', async () => {
    const { container } = render(<NameControl id="test" value={mockName} />);
    
    const firstNameInput = screen.getByLabelText(/first name/i);
    fireEvent.change(firstNameInput, { target: { value: 'Jane' } });
    
    await waitFor(() => {
      expect(container.querySelector('.is-modified')).toBeInTheDocument();
    });
  });
});

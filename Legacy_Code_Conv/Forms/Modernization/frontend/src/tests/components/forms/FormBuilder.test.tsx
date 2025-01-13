/**
 * Form builder component tests.
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { FormBuilder } from '../../../components/forms/FormBuilder';
import { FormSchema } from '../../../types/forms';


const mockSchema: FormSchema = {
  fields: [
    {
      id: '1',
      type: 'text',
      label: 'Name',
      required: true,
    },
  ],
};

describe('FormBuilder', () => {
  it('renders initial schema correctly', () => {
    render(
      <FormBuilder
        initialSchema={mockSchema}
        onChange={() => {}}
      />
    );
    
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Required')).toBeInTheDocument();
  });
  
  it('allows adding new fields', () => {
    const handleChange = jest.fn();
    render(
      <FormBuilder
        initialSchema={{ fields: [] }}
        onChange={handleChange}
      />
    );
    
    fireEvent.click(screen.getByText('Add Field'));
    fireEvent.click(screen.getByText('Text Field'));
    
    expect(handleChange).toHaveBeenCalledWith({
      fields: [
        expect.objectContaining({
          type: 'text',
          label: 'New Field',
        }),
      ],
    });
  });
  
  it('allows editing field properties', () => {
    const handleChange = jest.fn();
    render(
      <FormBuilder
        initialSchema={mockSchema}
        onChange={handleChange}
      />
    );
    
    fireEvent.click(screen.getByText('Name'));
    fireEvent.change(screen.getByLabelText('Field Label'), {
      target: { value: 'Full Name' },
    });
    
    expect(handleChange).toHaveBeenCalledWith({
      fields: [
        expect.objectContaining({
          id: '1',
          label: 'Full Name',
        }),
      ],
    });
  });
  
  it('allows reordering fields', () => {
    const handleChange = jest.fn();
    const twoFieldsSchema: FormSchema = {
      fields: [
        {
          id: '1',
          type: 'text',
          label: 'First',
        },
        {
          id: '2',
          type: 'text',
          label: 'Second',
        },
      ],
    };
    
    render(
      <FormBuilder
        initialSchema={twoFieldsSchema}
        onChange={handleChange}
      />
    );
    
    const firstField = screen.getByText('First');
    const secondField = screen.getByText('Second');
    
    // Simulate drag and drop
    fireEvent.dragStart(firstField);
    fireEvent.dragOver(secondField);
    fireEvent.drop(secondField);
    
    expect(handleChange).toHaveBeenCalledWith({
      fields: [
        expect.objectContaining({ id: '2' }),
        expect.objectContaining({ id: '1' }),
      ],
    });
  });
  
  it('validates field configuration', () => {
    render(
      <FormBuilder
        initialSchema={mockSchema}
        onChange={() => {}}
      />
    );
    
    fireEvent.click(screen.getByText('Name'));
    fireEvent.change(screen.getByLabelText('Field Label'), {
      target: { value: '' },
    });
    
    expect(screen.getByText('Label is required')).toBeInTheDocument();
  });
});

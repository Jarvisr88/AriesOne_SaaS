/**
 * Form validation hook tests
 */
import { renderHook, act } from '@testing-library/react';
import { useFormValidation } from '../../hooks/useFormValidation';
import { z } from 'zod';

describe('useFormValidation', () => {
  const testSchema = z.object({
    name: z.string().min(3, 'Name must be at least 3 characters'),
    email: z.string().email('Invalid email address'),
    age: z.number().min(18, 'Must be at least 18 years old')
  });

  const mockSubmit = jest.fn();

  beforeEach(() => {
    mockSubmit.mockClear();
  });

  it('initializes with default values', () => {
    const defaultValues = {
      name: 'John',
      email: 'john@example.com',
      age: 25
    };

    const { result } = renderHook(() =>
      useFormValidation({
        schema: testSchema,
        defaultValues,
        onSubmit: mockSubmit
      })
    );

    expect(result.current.getValues()).toEqual(defaultValues);
  });

  it('validates fields correctly', async () => {
    const { result } = renderHook(() =>
      useFormValidation({
        schema: testSchema,
        onSubmit: mockSubmit
      })
    );

    await act(async () => {
      await result.current.trigger('name');
    });

    expect(result.current.formState.errors.name?.message).toBe(
      'Name must be at least 3 characters'
    );
  });

  it('submits valid data successfully', async () => {
    const validData = {
      name: 'John',
      email: 'john@example.com',
      age: 25
    };

    const { result } = renderHook(() =>
      useFormValidation({
        schema: testSchema,
        defaultValues: validData,
        onSubmit: mockSubmit
      })
    );

    await act(async () => {
      await result.current.handleSubmit();
    });

    expect(mockSubmit).toHaveBeenCalledWith(validData);
  });

  it('handles submission errors', async () => {
    const error = new Error('Submission failed');
    mockSubmit.mockRejectedValue(error);

    const validData = {
      name: 'John',
      email: 'john@example.com',
      age: 25
    };

    const { result } = renderHook(() =>
      useFormValidation({
        schema: testSchema,
        defaultValues: validData,
        onSubmit: mockSubmit
      })
    );

    try {
      await act(async () => {
        await result.current.handleSubmit();
      });
    } catch (e) {
      expect(e).toBe(error);
    }
  });

  it('handles Zod validation errors', async () => {
    const { result } = renderHook(() =>
      useFormValidation({
        schema: testSchema,
        defaultValues: {
          name: 'Jo',
          email: 'invalid-email',
          age: 15
        },
        onSubmit: mockSubmit
      })
    );

    await act(async () => {
      await result.current.handleSubmit();
    });

    expect(result.current.formState.errors).toEqual({
      name: expect.objectContaining({
        message: 'Name must be at least 3 characters'
      }),
      email: expect.objectContaining({
        message: 'Invalid email address'
      }),
      age: expect.objectContaining({
        message: 'Must be at least 18 years old'
      })
    });

    expect(mockSubmit).not.toHaveBeenCalled();
  });
});

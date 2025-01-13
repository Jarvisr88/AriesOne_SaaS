/**
 * Custom hook for form validation with Zod
 */
import { useForm, UseFormProps } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useToastMessage } from './useToastMessage';
import { formatZodError } from '../utils/validationSchemas';

interface UseFormValidationProps<T extends z.ZodType> {
  schema: T;
  defaultValues?: Partial<z.infer<T>>;
  onSubmit: (data: z.infer<T>) => Promise<void>;
}

export const useFormValidation = <T extends z.ZodType>({
  schema,
  defaultValues,
  onSubmit
}: UseFormValidationProps<T>) => {
  const toast = useToastMessage();

  const formConfig: UseFormProps<z.infer<T>> = {
    resolver: zodResolver(schema),
    defaultValues
  };

  const form = useForm<z.infer<T>>(formConfig);

  const handleSubmit = async (data: z.infer<T>) => {
    try {
      await onSubmit(data);
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errors = formatZodError(error);
        Object.entries(errors).forEach(([field, message]) => {
          form.setError(field as any, {
            type: 'manual',
            message
          });
        });
      } else {
        toast.error(
          error.message || 'An error occurred while submitting the form'
        );
      }
      throw error;
    }
  };

  return {
    ...form,
    handleSubmit: form.handleSubmit(handleSubmit)
  };
};

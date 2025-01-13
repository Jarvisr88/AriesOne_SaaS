/**
 * Form renderer component.
 * 
 * This component renders a form based on its schema.
 */
import React from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  FormErrorMessage,
  Input,
  Select,
  Checkbox,
  VStack,
  useToast,
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { FormSchema } from '../../types/forms';


interface FormRendererProps {
  schema: FormSchema;
  onSubmit: (data: Record<string, any>) => void;
  initialData?: Record<string, any>;
}

export const FormRenderer: React.FC<FormRendererProps> = ({
  schema,
  onSubmit,
  initialData = {},
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm({
    defaultValues: initialData,
  });
  
  const toast = useToast();
  const watchedValues = watch();

  const isFieldVisible = (field: string): boolean => {
    if (!schema.validation?.dependencies) return true;
    
    const dependency = schema.validation.dependencies[field];
    if (!dependency) return true;
    
    const { field: depField, value, action } = dependency;
    const currentValue = watchedValues[depField];
    
    if (action === 'show') {
      return currentValue === value;
    } else if (action === 'hide') {
      return currentValue !== value;
    }
    
    return true;
  };

  const validateField = (value: any, field: string) => {
    if (!schema.validation?.custom) return true;
    
    const customValidation = schema.validation.custom[field];
    if (!customValidation) return true;
    
    try {
      // eslint-disable-next-line no-new-func
      const validate = new Function(
        'value',
        'formData',
        `return ${customValidation.condition}`
      );
      return validate(value, watchedValues) || customValidation.message;
    } catch (error) {
      console.error('Custom validation error:', error);
      return 'Invalid validation condition';
    }
  };

  const onSubmitHandler = (data: Record<string, any>) => {
    try {
      onSubmit(data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to submit form',
        status: 'error',
        duration: 3000,
      });
    }
  };

  return (
    <Box
      as="form"
      onSubmit={handleSubmit(onSubmitHandler)}
      width="100%"
    >
      <VStack spacing={4} align="stretch">
        {schema.fields.map((field) => {
          if (!isFieldVisible(field.name)) return null;
          
          const isRequired = field.required ||
            schema.validation?.dependencies?.[field.name]?.action === 'require';
          
          return (
            <FormControl
              key={field.name}
              isRequired={isRequired}
              isInvalid={!!errors[field.name]}
            >
              <FormLabel>{field.label}</FormLabel>
              
              {field.type === 'text' && (
                <Input
                  {...register(field.name, {
                    required: isRequired && 'This field is required',
                    pattern: field.validation?.pattern
                      ? {
                          value: new RegExp(field.validation.pattern),
                          message: 'Invalid format',
                        }
                      : undefined,
                    validate: (value) => validateField(value, field.name),
                  })}
                  type="text"
                />
              )}
              
              {field.type === 'number' && (
                <Input
                  {...register(field.name, {
                    required: isRequired && 'This field is required',
                    min: {
                      value: field.validation?.min || -Infinity,
                      message: `Minimum value is ${field.validation?.min}`,
                    },
                    max: {
                      value: field.validation?.max || Infinity,
                      message: `Maximum value is ${field.validation?.max}`,
                    },
                    validate: (value) => validateField(value, field.name),
                  })}
                  type="number"
                />
              )}
              
              {field.type === 'select' && (
                <Select
                  {...register(field.name, {
                    required: isRequired && 'This field is required',
                    validate: (value) => validateField(value, field.name),
                  })}
                >
                  <option value="">Select...</option>
                  {field.options?.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </Select>
              )}
              
              {field.type === 'date' && (
                <Input
                  {...register(field.name, {
                    required: isRequired && 'This field is required',
                    validate: (value) => validateField(value, field.name),
                  })}
                  type="date"
                />
              )}
              
              {field.type === 'checkbox' && (
                <Checkbox
                  {...register(field.name, {
                    validate: (value) => validateField(value, field.name),
                  })}
                >
                  {field.label}
                </Checkbox>
              )}
              
              <FormErrorMessage>
                {errors[field.name]?.message as string}
              </FormErrorMessage>
            </FormControl>
          );
        })}
        
        <Button
          mt={4}
          colorScheme="blue"
          type="submit"
          width="full"
        >
          Submit
        </Button>
      </VStack>
    </Box>
  );
};

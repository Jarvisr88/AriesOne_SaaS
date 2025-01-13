import React from 'react';
import {
  FormControl,
  FormLabel,
  FormErrorMessage,
  FormHelperText,
  Input,
  Textarea,
  Select,
  Switch,
  Checkbox,
  Radio,
  RadioGroup,
  Stack,
  Button,
  VStack,
  useColorModeValue,
} from '@chakra-ui/react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

interface Field {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'textarea' | 'select' | 'switch' | 'checkbox' | 'radio';
  options?: { value: string; label: string }[];
  placeholder?: string;
  helperText?: string;
  required?: boolean;
  validation?: z.ZodType<any>;
}

interface AccessibleFormProps {
  fields: Field[];
  onSubmit: (data: any) => void;
  submitLabel?: string;
  schema?: z.ZodType<any>;
}

export const AccessibleForm: React.FC<AccessibleFormProps> = ({
  fields,
  onSubmit,
  submitLabel = 'Submit',
  schema,
}) => {
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: schema ? zodResolver(schema) : undefined,
  });

  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const renderField = (field: Field) => {
    const commonProps = {
      id: field.name,
      placeholder: field.placeholder,
      'aria-describedby': `${field.name}-helper-text`,
      isRequired: field.required,
      bg: bg,
      borderColor: borderColor,
    };

    switch (field.type) {
      case 'textarea':
        return (
          <Controller
            name={field.name}
            control={control}
            defaultValue=""
            render={({ field: { onChange, value } }) => (
              <Textarea {...commonProps} value={value} onChange={onChange} />
            )}
          />
        );

      case 'select':
        return (
          <Controller
            name={field.name}
            control={control}
            defaultValue=""
            render={({ field: { onChange, value } }) => (
              <Select {...commonProps} value={value} onChange={onChange}>
                {field.options?.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </Select>
            )}
          />
        );

      case 'switch':
        return (
          <Controller
            name={field.name}
            control={control}
            defaultValue={false}
            render={({ field: { onChange, value } }) => (
              <Switch {...commonProps} isChecked={value} onChange={onChange} />
            )}
          />
        );

      case 'checkbox':
        return (
          <Controller
            name={field.name}
            control={control}
            defaultValue={false}
            render={({ field: { onChange, value } }) => (
              <Checkbox {...commonProps} isChecked={value} onChange={onChange}>
                {field.label}
              </Checkbox>
            )}
          />
        );

      case 'radio':
        return (
          <Controller
            name={field.name}
            control={control}
            defaultValue=""
            render={({ field: { onChange, value } }) => (
              <RadioGroup value={value} onChange={onChange}>
                <Stack direction="row">
                  {field.options?.map((option) => (
                    <Radio key={option.value} value={option.value}>
                      {option.label}
                    </Radio>
                  ))}
                </Stack>
              </RadioGroup>
            )}
          />
        );

      default:
        return (
          <Controller
            name={field.name}
            control={control}
            defaultValue=""
            render={({ field: { onChange, value } }) => (
              <Input
                {...commonProps}
                type={field.type}
                value={value}
                onChange={onChange}
              />
            )}
          />
        );
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <VStack spacing={4} align="stretch">
        {fields.map((field) => (
          <FormControl
            key={field.name}
            isInvalid={!!errors[field.name]}
            isRequired={field.required}
          >
            <FormLabel htmlFor={field.name}>{field.label}</FormLabel>
            {renderField(field)}
            {field.helperText && (
              <FormHelperText id={`${field.name}-helper-text`}>
                {field.helperText}
              </FormHelperText>
            )}
            <FormErrorMessage>
              {errors[field.name]?.message as string}
            </FormErrorMessage>
          </FormControl>
        ))}
        <Button
          mt={4}
          colorScheme="brand"
          isLoading={isSubmitting}
          type="submit"
          width="full"
        >
          {submitLabel}
        </Button>
      </VStack>
    </form>
  );
};

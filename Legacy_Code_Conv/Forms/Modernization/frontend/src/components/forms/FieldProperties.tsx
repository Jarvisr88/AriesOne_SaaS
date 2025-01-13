/**
 * Field properties component.
 * 
 * This component provides a form for editing field properties.
 */
import React from 'react';
import {
  Box,
  FormControl,
  FormLabel,
  Input,
  Select,
  Switch,
  VStack,
  FormHelperText,
} from '@chakra-ui/react';
import { FormField } from '../../types/forms';


interface FieldPropertiesProps {
  field: FormField;
  onChange: (field: FormField) => void;
}

export const FieldProperties: React.FC<FieldPropertiesProps> = ({
  field,
  onChange,
}) => {
  const handleChange = (
    key: keyof FormField,
    value: string | boolean | string[]
  ) => {
    onChange({
      ...field,
      [key]: value,
    });
  };

  return (
    <VStack spacing={4} align="stretch">
      <Box>
        <FormControl>
          <FormLabel>Field Label</FormLabel>
          <Input
            value={field.label}
            onChange={(e) => handleChange('label', e.target.value)}
          />
          <FormHelperText>
            Display name for the field
          </FormHelperText>
        </FormControl>
      </Box>

      <Box>
        <FormControl>
          <FormLabel>Field Name</FormLabel>
          <Input
            value={field.name}
            onChange={(e) => handleChange('name', e.target.value)}
          />
          <FormHelperText>
            Unique identifier for the field
          </FormHelperText>
        </FormControl>
      </Box>

      <Box>
        <FormControl>
          <FormLabel>Field Type</FormLabel>
          <Select
            value={field.type}
            onChange={(e) => handleChange('type', e.target.value)}
          >
            <option value="text">Text</option>
            <option value="number">Number</option>
            <option value="select">Select</option>
            <option value="date">Date</option>
            <option value="checkbox">Checkbox</option>
          </Select>
          <FormHelperText>
            Type of input field
          </FormHelperText>
        </FormControl>
      </Box>

      {field.type === 'select' && (
        <Box>
          <FormControl>
            <FormLabel>Options</FormLabel>
            <Input
              value={field.options?.join(', ') || ''}
              onChange={(e) => handleChange(
                'options',
                e.target.value.split(',').map((s) => s.trim())
              )}
              placeholder="Option 1, Option 2, Option 3"
            />
            <FormHelperText>
              Comma-separated list of options
            </FormHelperText>
          </FormControl>
        </Box>
      )}

      {(field.type === 'text' || field.type === 'number') && (
        <Box>
          <FormControl>
            <FormLabel>Default Value</FormLabel>
            <Input
              value={field.defaultValue || ''}
              onChange={(e) => handleChange(
                'defaultValue',
                field.type === 'number'
                  ? Number(e.target.value)
                  : e.target.value
              )}
              type={field.type}
            />
            <FormHelperText>
              Initial value for the field
            </FormHelperText>
          </FormControl>
        </Box>
      )}

      {field.type === 'number' && (
        <>
          <Box>
            <FormControl>
              <FormLabel>Minimum Value</FormLabel>
              <Input
                type="number"
                value={field.validation?.min || ''}
                onChange={(e) => handleChange('validation', {
                  ...field.validation,
                  min: Number(e.target.value),
                })}
              />
            </FormControl>
          </Box>

          <Box>
            <FormControl>
              <FormLabel>Maximum Value</FormLabel>
              <Input
                type="number"
                value={field.validation?.max || ''}
                onChange={(e) => handleChange('validation', {
                  ...field.validation,
                  max: Number(e.target.value),
                })}
              />
            </FormControl>
          </Box>
        </>
      )}

      {field.type === 'text' && (
        <Box>
          <FormControl>
            <FormLabel>Pattern</FormLabel>
            <Input
              value={field.validation?.pattern || ''}
              onChange={(e) => handleChange('validation', {
                ...field.validation,
                pattern: e.target.value,
              })}
              placeholder="Regular expression"
            />
            <FormHelperText>
              Validation pattern (regex)
            </FormHelperText>
          </FormControl>
        </Box>
      )}

      <Box>
        <FormControl display="flex" alignItems="center">
          <FormLabel mb="0">
            Required Field
          </FormLabel>
          <Switch
            isChecked={field.required}
            onChange={(e) => handleChange(
              'required',
              e.target.checked
            )}
          />
        </FormControl>
      </Box>
    </VStack>
  );
};

/**
 * Form builder component.
 * 
 * This component provides a drag-and-drop interface for building forms.
 */
import React, { useState } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { FormField, FormSchema } from '../../types/forms';
import { SortableField } from './SortableField';
import { FieldProperties } from './FieldProperties';
import {
  Box,
  Button,
  Flex,
  IconButton,
  Text,
  useColorModeValue,
  useToast,
} from '@chakra-ui/react';
import { AddIcon } from '@chakra-ui/icons';


interface FormBuilderProps {
  initialSchema?: FormSchema;
  onChange?: (schema: FormSchema) => void;
  onSave?: (schema: FormSchema) => void;
}

export const FormBuilder: React.FC<FormBuilderProps> = ({
  initialSchema,
  onChange,
  onSave,
}) => {
  const [schema, setSchema] = useState<FormSchema>(
    initialSchema || { fields: [] }
  );
  const [selectedField, setSelectedField] = useState<number | null>(null);
  
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    
    if (active.id !== over.id) {
      const oldIndex = schema.fields.findIndex(
        (field) => `field-${field.name}` === active.id
      );
      const newIndex = schema.fields.findIndex(
        (field) => `field-${field.name}` === over.id
      );
      
      const newFields = arrayMove(schema.fields, oldIndex, newIndex);
      const newSchema = { ...schema, fields: newFields };
      
      setSchema(newSchema);
      onChange?.(newSchema);
    }
  };

  const addField = () => {
    const fieldCount = schema.fields.length;
    const newField: FormField = {
      name: `field_${fieldCount + 1}`,
      label: `Field ${fieldCount + 1}`,
      type: 'text',
      required: false,
    };
    
    const newSchema = {
      ...schema,
      fields: [...schema.fields, newField],
    };
    
    setSchema(newSchema);
    setSelectedField(fieldCount);
    onChange?.(newSchema);
    
    toast({
      title: 'Field added',
      description: `Added new field: ${newField.label}`,
      status: 'success',
      duration: 2000,
    });
  };

  const updateField = (index: number, field: FormField) => {
    const newFields = [...schema.fields];
    newFields[index] = field;
    
    const newSchema = { ...schema, fields: newFields };
    setSchema(newSchema);
    onChange?.(newSchema);
  };

  const deleteField = (index: number) => {
    const fieldName = schema.fields[index].label;
    const newFields = schema.fields.filter((_, i) => i !== index);
    
    const newSchema = { ...schema, fields: newFields };
    setSchema(newSchema);
    setSelectedField(null);
    onChange?.(newSchema);
    
    toast({
      title: 'Field deleted',
      description: `Deleted field: ${fieldName}`,
      status: 'info',
      duration: 2000,
    });
  };

  const handleSave = () => {
    if (schema.fields.length === 0) {
      toast({
        title: 'Error',
        description: 'Form must have at least one field',
        status: 'error',
        duration: 3000,
      });
      return;
    }
    
    // Validate field names are unique
    const names = new Set();
    for (const field of schema.fields) {
      if (names.has(field.name)) {
        toast({
          title: 'Error',
          description: `Duplicate field name: ${field.name}`,
          status: 'error',
          duration: 3000,
        });
        return;
      }
      names.add(field.name);
    }
    
    onSave?.(schema);
  };

  return (
    <Flex gap={4}>
      <Box
        flex={2}
        p={4}
        bg={bgColor}
        borderRadius="md"
        borderWidth={1}
        borderColor={borderColor}
      >
        <Flex justify="space-between" align="center" mb={4}>
          <Text fontSize="lg" fontWeight="bold">
            Form Fields
          </Text>
          <IconButton
            aria-label="Add field"
            icon={<AddIcon />}
            onClick={addField}
            colorScheme="blue"
            size="sm"
          />
        </Flex>
        
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={schema.fields.map((f) => `field-${f.name}`)}
            strategy={verticalListSortingStrategy}
          >
            {schema.fields.map((field, index) => (
              <SortableField
                key={`field-${field.name}`}
                id={`field-${field.name}`}
                field={field}
                isSelected={selectedField === index}
                onClick={() => setSelectedField(index)}
                onDelete={() => deleteField(index)}
              />
            ))}
          </SortableContext>
        </DndContext>
        
        {schema.fields.length === 0 && (
          <Text
            textAlign="center"
            color="gray.500"
            fontSize="sm"
            mt={4}
          >
            No fields added yet. Click the + button to add a field.
          </Text>
        )}
        
        <Button
          mt={4}
          colorScheme="blue"
          width="full"
          onClick={handleSave}
        >
          Save Form
        </Button>
      </Box>
      
      {selectedField !== null && (
        <Box
          flex={1}
          p={4}
          bg={bgColor}
          borderRadius="md"
          borderWidth={1}
          borderColor={borderColor}
        >
          <FieldProperties
            field={schema.fields[selectedField]}
            onChange={(field) => updateField(selectedField, field)}
          />
        </Box>
      )}
    </Flex>
  );
};

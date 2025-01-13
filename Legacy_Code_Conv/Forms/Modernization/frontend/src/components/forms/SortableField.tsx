/**
 * Sortable field component.
 * 
 * This component renders a draggable form field in the form builder.
 */
import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  Box,
  Flex,
  IconButton,
  Text,
  useColorModeValue,
} from '@chakra-ui/react';
import {
  DragHandleIcon,
  DeleteIcon,
} from '@chakra-ui/icons';
import { FormField } from '../../types/forms';


interface SortableFieldProps {
  id: string;
  field: FormField;
  isSelected: boolean;
  onClick: () => void;
  onDelete: () => void;
}

export const SortableField: React.FC<SortableFieldProps> = ({
  id,
  field,
  isSelected,
  onClick,
  onDelete,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id });
  
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };
  
  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const selectedBgColor = useColorModeValue('blue.50', 'blue.900');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const selectedBorderColor = useColorModeValue('blue.200', 'blue.600');
  
  return (
    <Box
      ref={setNodeRef}
      style={style}
      onClick={onClick}
      cursor="pointer"
      p={3}
      mb={2}
      bg={isSelected ? selectedBgColor : bgColor}
      borderWidth={1}
      borderColor={isSelected ? selectedBorderColor : borderColor}
      borderRadius="md"
      transition="all 0.2s"
      _hover={{
        bg: isSelected ? selectedBgColor : useColorModeValue('gray.100', 'gray.600'),
      }}
    >
      <Flex align="center" justify="space-between">
        <Flex align="center" flex={1}>
          <IconButton
            {...attributes}
            {...listeners}
            aria-label="Drag handle"
            icon={<DragHandleIcon />}
            variant="ghost"
            size="sm"
            cursor="grab"
            mr={2}
          />
          
          <Box flex={1}>
            <Text fontWeight="medium">
              {field.label}
            </Text>
            <Text fontSize="sm" color="gray.500">
              {field.type}
              {field.required && ' • Required'}
            </Text>
          </Box>
        </Flex>
        
        <IconButton
          aria-label="Delete field"
          icon={<DeleteIcon />}
          variant="ghost"
          size="sm"
          colorScheme="red"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
        />
      </Flex>
    </Box>
  );
};

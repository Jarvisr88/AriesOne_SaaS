/**
 * Form create page.
 * 
 * This page provides a form builder interface for creating new forms.
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Textarea,
  useToast,
  VStack,
} from '@chakra-ui/react';
import { FormBuilder } from '../../components/forms/FormBuilder';
import { useCreateForm } from '../../hooks/useFormQuery';
import { FormSchema } from '../../types/forms';


export const FormCreate: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const createForm = useCreateForm();
  const [name, setName] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [schema, setSchema] = React.useState<FormSchema>({ fields: [] });
  
  const handleSubmit = async () => {
    if (!name.trim()) {
      toast({
        title: 'Error',
        description: 'Form name is required',
        status: 'error',
        duration: 3000,
      });
      return;
    }
    
    if (schema.fields.length === 0) {
      toast({
        title: 'Error',
        description: 'Form must have at least one field',
        status: 'error',
        duration: 3000,
      });
      return;
    }
    
    try {
      const form = await createForm.mutateAsync({
        name,
        description,
        schema,
      });
      
      toast({
        title: 'Success',
        description: 'Form created successfully',
        status: 'success',
        duration: 3000,
      });
      
      navigate(`/forms/${form.id}`);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create form',
        status: 'error',
        duration: 3000,
      });
    }
  };
  
  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Create Form</Heading>
        <Button
          onClick={() => navigate('/forms')}
          variant="outline"
        >
          Cancel
        </Button>
      </Flex>
      
      <VStack spacing={8} align="stretch">
        <Box>
          <FormControl isRequired>
            <FormLabel>Form Name</FormLabel>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter form name"
            />
          </FormControl>
          
          <FormControl mt={4}>
            <FormLabel>Description</FormLabel>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter form description"
              rows={3}
            />
          </FormControl>
        </Box>
        
        <Box>
          <FormBuilder
            initialSchema={schema}
            onChange={setSchema}
          />
        </Box>
        
        <Flex justify="flex-end" gap={4}>
          <Button
            onClick={() => navigate('/forms')}
            variant="ghost"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            colorScheme="blue"
            isLoading={createForm.isPending}
          >
            Create Form
          </Button>
        </Flex>
      </VStack>
    </Box>
  );
};

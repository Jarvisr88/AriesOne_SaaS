/**
 * Form edit page.
 * 
 * This page provides a form builder interface for editing existing forms.
 */
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
  Spinner,
} from '@chakra-ui/react';
import { FormBuilder } from '../../components/forms/FormBuilder';
import {
  useFormDetail,
  useUpdateForm,
} from '../../hooks/useFormQuery';
import { FormSchema } from '../../types/forms';


export const FormEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  
  const formId = parseInt(id || '0');
  const { data: form, isLoading } = useFormDetail(formId);
  const updateForm = useUpdateForm();
  
  const [name, setName] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [schema, setSchema] = React.useState<FormSchema>({ fields: [] });
  
  React.useEffect(() => {
    if (form) {
      setName(form.name);
      setDescription(form.description || '');
      setSchema(form.schema);
    }
  }, [form]);
  
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
      await updateForm.mutateAsync({
        id: formId,
        data: {
          name,
          description,
          schema,
        },
      });
      
      toast({
        title: 'Success',
        description: 'Form updated successfully',
        status: 'success',
        duration: 3000,
      });
      
      navigate(`/forms/${formId}`);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update form',
        status: 'error',
        duration: 3000,
      });
    }
  };
  
  if (isLoading) {
    return (
      <Flex justify="center" align="center" minH="200px">
        <Spinner />
      </Flex>
    );
  }
  
  if (!form) {
    return (
      <Box
        p={4}
        bg="red.50"
        color="red.500"
        borderRadius="md"
        textAlign="center"
      >
        Form not found
      </Box>
    );
  }
  
  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Edit Form</Heading>
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
            isLoading={updateForm.isPending}
          >
            Save Changes
          </Button>
        </Flex>
      </VStack>
    </Box>
  );
};

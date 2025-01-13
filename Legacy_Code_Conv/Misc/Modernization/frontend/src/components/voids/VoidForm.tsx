/**
 * Void form component
 */
import React from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  VStack,
  useToast
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { VoidCreate } from '../../types';
import { useCreateVoid } from '../../hooks/useMiscApi';

interface VoidFormProps {
  onSuccess?: (voidRequest: VoidCreate) => void;
}

export const VoidForm: React.FC<VoidFormProps> = ({
  onSuccess
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<VoidCreate>();

  const toast = useToast();
  const { createVoid, loading } = useCreateVoid();

  const onSubmit = async (data: VoidCreate) => {
    try {
      await createVoid(data);
      toast({
        title: 'Void request created',
        status: 'success',
        duration: 3000
      });
      reset();
      onSuccess?.(data);
    } catch (error) {
      toast({
        title: 'Error creating void request',
        description: error.message,
        status: 'error',
        duration: 5000
      });
    }
  };

  return (
    <Box as="form" onSubmit={handleSubmit(onSubmit)}>
      <VStack spacing={4} align="stretch">
        <FormControl isInvalid={!!errors.amount}>
          <FormLabel>Amount</FormLabel>
          <Input
            type="number"
            step="0.01"
            {...register('amount', {
              required: 'Amount is required',
              min: {
                value: 0.01,
                message: 'Amount must be greater than 0'
              }
            })}
          />
        </FormControl>

        <FormControl isInvalid={!!errors.reason}>
          <FormLabel>Reason</FormLabel>
          <Textarea
            {...register('reason', {
              required: 'Reason is required',
              minLength: {
                value: 10,
                message: 'Reason must be at least 10 characters'
              }
            })}
            placeholder="Enter reason for void request"
          />
        </FormControl>

        <Button
          type="submit"
          colorScheme="blue"
          isLoading={loading}
          loadingText="Creating..."
        >
          Submit Void Request
        </Button>
      </VStack>
    </Box>
  );
};

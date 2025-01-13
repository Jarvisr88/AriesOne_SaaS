/**
 * Deposit form component
 */
import React from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  VStack,
  useToast
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { DepositCreate } from '../../types';
import { useCreateDeposit } from '../../hooks/useMiscApi';

interface DepositFormProps {
  onSuccess?: (deposit: DepositCreate) => void;
}

export const DepositForm: React.FC<DepositFormProps> = ({
  onSuccess
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<DepositCreate>();

  const toast = useToast();
  const { createDeposit, loading } = useCreateDeposit();

  const onSubmit = async (data: DepositCreate) => {
    try {
      await createDeposit(data);
      toast({
        title: 'Deposit created',
        status: 'success',
        duration: 3000
      });
      reset();
      onSuccess?.(data);
    } catch (error) {
      toast({
        title: 'Error creating deposit',
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

        <FormControl isInvalid={!!errors.paymentMethod}>
          <FormLabel>Payment Method</FormLabel>
          <Select
            {...register('paymentMethod', {
              required: 'Payment method is required'
            })}
          >
            <option value="">Select payment method</option>
            <option value="cash">Cash</option>
            <option value="check">Check</option>
            <option value="credit">Credit Card</option>
            <option value="debit">Debit Card</option>
            <option value="transfer">Bank Transfer</option>
          </Select>
        </FormControl>

        <FormControl isInvalid={!!errors.customerId}>
          <FormLabel>Customer ID</FormLabel>
          <Input
            type="number"
            {...register('customerId', {
              required: 'Customer ID is required',
              min: {
                value: 1,
                message: 'Invalid customer ID'
              }
            })}
          />
        </FormControl>

        <Button
          type="submit"
          colorScheme="blue"
          isLoading={loading}
          loadingText="Creating..."
        >
          Create Deposit
        </Button>
      </VStack>
    </Box>
  );
};

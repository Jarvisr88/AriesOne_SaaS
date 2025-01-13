/**
 * Purchase order form component
 */
import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  HStack,
  IconButton,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useToast
} from '@chakra-ui/react';
import { DeleteIcon } from '@chakra-ui/icons';
import { useForm, useFieldArray } from 'react-hook-form';
import {
  PurchaseOrderCreate,
  PurchaseOrderItem
} from '../../types';
import { useCreatePurchaseOrder } from '../../hooks/useMiscApi';

interface PurchaseOrderFormProps {
  onSuccess?: (order: PurchaseOrderCreate) => void;
}

export const PurchaseOrderForm: React.FC<PurchaseOrderFormProps> = ({
  onSuccess
}) => {
  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors },
    reset
  } = useForm<PurchaseOrderCreate>({
    defaultValues: {
      items: [{ name: '', quantity: 1, price: 0 }]
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items'
  });

  const toast = useToast();
  const { createPurchaseOrder, loading } = useCreatePurchaseOrder();

  // Calculate totals
  const items = watch('items');
  const total = items.reduce(
    (sum, item) => sum + (item.quantity * item.price),
    0
  );

  const onSubmit = async (data: PurchaseOrderCreate) => {
    try {
      await createPurchaseOrder(data);
      toast({
        title: 'Purchase order created',
        status: 'success',
        duration: 3000
      });
      reset();
      onSuccess?.(data);
    } catch (error) {
      toast({
        title: 'Error creating purchase order',
        description: error.message,
        status: 'error',
        duration: 5000
      });
    }
  };

  return (
    <Box as="form" onSubmit={handleSubmit(onSubmit)}>
      <VStack spacing={4} align="stretch">
        <FormControl isInvalid={!!errors.vendorId}>
          <FormLabel>Vendor ID</FormLabel>
          <Input
            type="number"
            {...register('vendorId', {
              required: 'Vendor ID is required',
              min: {
                value: 1,
                message: 'Invalid vendor ID'
              }
            })}
          />
        </FormControl>

        <Box>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Item</Th>
                <Th>Quantity</Th>
                <Th>Price</Th>
                <Th>Total</Th>
                <Th></Th>
              </Tr>
            </Thead>
            <Tbody>
              {fields.map((field, index) => (
                <Tr key={field.id}>
                  <Td>
                    <Input
                      {...register(`items.${index}.name`, {
                        required: 'Item name is required'
                      })}
                      placeholder="Item name"
                    />
                  </Td>
                  <Td>
                    <Input
                      type="number"
                      {...register(`items.${index}.quantity`, {
                        required: 'Quantity is required',
                        min: {
                          value: 1,
                          message: 'Quantity must be at least 1'
                        }
                      })}
                    />
                  </Td>
                  <Td>
                    <Input
                      type="number"
                      step="0.01"
                      {...register(`items.${index}.price`, {
                        required: 'Price is required',
                        min: {
                          value: 0.01,
                          message: 'Price must be greater than 0'
                        }
                      })}
                    />
                  </Td>
                  <Td>
                    ${(items[index]?.quantity * items[index]?.price).toFixed(2)}
                  </Td>
                  <Td>
                    <IconButton
                      aria-label="Remove item"
                      icon={<DeleteIcon />}
                      onClick={() => remove(index)}
                      disabled={fields.length === 1}
                    />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>

          <Button
            mt={2}
            onClick={() => append({
              name: '',
              quantity: 1,
              price: 0
            })}
          >
            Add Item
          </Button>
        </Box>

        <Box borderTop="1px" pt={4}>
          <HStack justify="space-between">
            <Text fontSize="lg" fontWeight="bold">
              Total:
            </Text>
            <Text fontSize="lg">
              ${total.toFixed(2)}
            </Text>
          </HStack>
        </Box>

        <Button
          type="submit"
          colorScheme="blue"
          isLoading={loading}
          loadingText="Creating..."
        >
          Create Purchase Order
        </Button>
      </VStack>
    </Box>
  );
};

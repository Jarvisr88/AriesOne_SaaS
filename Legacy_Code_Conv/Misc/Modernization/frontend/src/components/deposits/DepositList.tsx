/**
 * Deposit list component
 */
import React from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Button,
  HStack,
  useToast,
  Spinner,
  Text
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { Link as RouterLink } from 'react-router-dom';
import { depositsApi } from '../../api/misc';
import { Deposit } from '../../types';

const statusColors = {
  pending: 'yellow',
  completed: 'green',
  failed: 'red'
};

export const DepositList: React.FC = () => {
  const toast = useToast();

  const {
    data: deposits,
    isLoading,
    error
  } = useQuery<Deposit[]>(
    ['deposits'],
    () => depositsApi.list(),
    {
      onError: (error) => {
        toast({
          title: 'Error loading deposits',
          description: error.message,
          status: 'error',
          duration: 5000
        });
      }
    }
  );

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minH="200px"
      >
        <Spinner />
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        p={4}
        bg="red.50"
        color="red.500"
        borderRadius="md"
      >
        <Text>Error loading deposits</Text>
      </Box>
    );
  }

  return (
    <Box>
      <HStack
        justify="space-between"
        mb={4}
      >
        <Text fontSize="xl" fontWeight="bold">
          Deposits
        </Text>
        <Button
          as={RouterLink}
          to="/deposits/new"
          colorScheme="blue"
        >
          New Deposit
        </Button>
      </HStack>

      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>ID</Th>
            <Th>Amount</Th>
            <Th>Payment Method</Th>
            <Th>Customer ID</Th>
            <Th>Status</Th>
            <Th>Created</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {deposits?.map((deposit) => (
            <Tr key={deposit.id}>
              <Td>{deposit.id}</Td>
              <Td>
                ${deposit.amount.toFixed(2)}
              </Td>
              <Td>
                {deposit.paymentMethod}
              </Td>
              <Td>{deposit.customerId}</Td>
              <Td>
                <Badge
                  colorScheme={
                    statusColors[deposit.status]
                  }
                >
                  {deposit.status}
                </Badge>
              </Td>
              <Td>
                {new Date(
                  deposit.createdAt
                ).toLocaleDateString()}
              </Td>
              <Td>
                <HStack spacing={2}>
                  <Button
                    as={RouterLink}
                    to={`/deposits/${deposit.id}`}
                    size="sm"
                    variant="outline"
                  >
                    View
                  </Button>
                  <Button
                    as={RouterLink}
                    to={`/deposits/${deposit.id}/edit`}
                    size="sm"
                    variant="outline"
                    colorScheme="blue"
                  >
                    Edit
                  </Button>
                </HStack>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

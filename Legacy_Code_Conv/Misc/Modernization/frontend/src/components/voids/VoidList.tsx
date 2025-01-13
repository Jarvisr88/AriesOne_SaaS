/**
 * Void list component
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
  Text,
  Tooltip
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { Link as RouterLink } from 'react-router-dom';
import { voidsApi } from '../../api/misc';
import { Void } from '../../types';

const statusColors = {
  pending: 'yellow',
  approved: 'green',
  rejected: 'red'
};

export const VoidList: React.FC = () => {
  const toast = useToast();

  const {
    data: voids,
    isLoading,
    error
  } = useQuery<Void[]>(
    ['voids'],
    () => voidsApi.list(),
    {
      onError: (error) => {
        toast({
          title: 'Error loading voids',
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
        <Text>Error loading void requests</Text>
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
          Void Requests
        </Text>
        <Button
          as={RouterLink}
          to="/voids/new"
          colorScheme="blue"
        >
          New Void Request
        </Button>
      </HStack>

      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>ID</Th>
            <Th>Amount</Th>
            <Th>Reason</Th>
            <Th>Status</Th>
            <Th>Created By</Th>
            <Th>Created</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {voids?.map((voidRequest) => (
            <Tr key={voidRequest.id}>
              <Td>{voidRequest.id}</Td>
              <Td>
                ${voidRequest.amount.toFixed(2)}
              </Td>
              <Td>
                <Tooltip
                  label={voidRequest.reason}
                  placement="top"
                >
                  <Text
                    maxW="200px"
                    isTruncated
                  >
                    {voidRequest.reason}
                  </Text>
                </Tooltip>
              </Td>
              <Td>
                <Badge
                  colorScheme={
                    statusColors[voidRequest.status]
                  }
                >
                  {voidRequest.status}
                </Badge>
              </Td>
              <Td>{voidRequest.createdBy}</Td>
              <Td>
                {new Date(
                  voidRequest.createdAt
                ).toLocaleDateString()}
              </Td>
              <Td>
                <HStack spacing={2}>
                  <Button
                    as={RouterLink}
                    to={`/voids/${voidRequest.id}`}
                    size="sm"
                    variant="outline"
                  >
                    View
                  </Button>
                  {voidRequest.status === 'pending' && (
                    <Button
                      as={RouterLink}
                      to={`/voids/${voidRequest.id}/edit`}
                      size="sm"
                      variant="outline"
                      colorScheme="blue"
                    >
                      Edit
                    </Button>
                  )}
                </HStack>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

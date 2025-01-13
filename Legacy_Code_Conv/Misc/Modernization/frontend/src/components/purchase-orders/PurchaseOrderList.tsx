/**
 * Purchase order list component
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
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton
} from '@chakra-ui/react';
import { ChevronDownIcon } from '@chakra-ui/icons';
import { useQuery } from '@tanstack/react-query';
import { Link as RouterLink } from 'react-router-dom';
import { purchaseOrdersApi } from '../../api/misc';
import { PurchaseOrder } from '../../types';

const statusColors = {
  draft: 'gray',
  submitted: 'yellow',
  approved: 'green',
  received: 'blue'
};

export const PurchaseOrderList: React.FC = () => {
  const toast = useToast();

  const {
    data: orders,
    isLoading,
    error
  } = useQuery<PurchaseOrder[]>(
    ['purchase-orders'],
    () => purchaseOrdersApi.list(),
    {
      onError: (error) => {
        toast({
          title: 'Error loading purchase orders',
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
        <Text>Error loading purchase orders</Text>
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
          Purchase Orders
        </Text>
        <Button
          as={RouterLink}
          to="/purchase-orders/new"
          colorScheme="blue"
        >
          New Purchase Order
        </Button>
      </HStack>

      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>ID</Th>
            <Th>Vendor ID</Th>
            <Th>Items</Th>
            <Th>Total</Th>
            <Th>Status</Th>
            <Th>Created</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {orders?.map((order) => (
            <Tr key={order.id}>
              <Td>{order.id}</Td>
              <Td>{order.vendorId}</Td>
              <Td>{order.items.length} items</Td>
              <Td>
                ${order.total.toFixed(2)}
              </Td>
              <Td>
                <Badge
                  colorScheme={
                    statusColors[order.status]
                  }
                >
                  {order.status}
                </Badge>
              </Td>
              <Td>
                {new Date(
                  order.createdAt
                ).toLocaleDateString()}
              </Td>
              <Td>
                <Menu>
                  <MenuButton
                    as={IconButton}
                    icon={<ChevronDownIcon />}
                    variant="outline"
                    size="sm"
                  />
                  <MenuList>
                    <MenuItem
                      as={RouterLink}
                      to={`/purchase-orders/${order.id}`}
                    >
                      View Details
                    </MenuItem>
                    {order.status === 'draft' && (
                      <MenuItem
                        as={RouterLink}
                        to={`/purchase-orders/${order.id}/edit`}
                      >
                        Edit
                      </MenuItem>
                    )}
                    {order.status === 'approved' && (
                      <MenuItem
                        as={RouterLink}
                        to={`/purchase-orders/${order.id}/receive`}
                      >
                        Receive Items
                      </MenuItem>
                    )}
                    {order.status === 'draft' && (
                      <MenuItem
                        onClick={() => {
                          // Submit order
                        }}
                      >
                        Submit for Approval
                      </MenuItem>
                    )}
                  </MenuList>
                </Menu>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

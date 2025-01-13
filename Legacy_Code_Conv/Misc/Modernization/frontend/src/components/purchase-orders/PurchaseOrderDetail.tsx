/**
 * Purchase order detail component
 */
import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Button,
  Spinner,
  useToast,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Grid,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  ButtonGroup,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import { purchaseOrdersApi } from '../../api/misc';
import { PurchaseOrder } from '../../types';

const statusColors = {
  draft: 'gray',
  submitted: 'yellow',
  approved: 'green',
  received: 'blue'
};

const FieldDisplay: React.FC<{
  label: string;
  value: string | number;
}> = ({ label, value }) => (
  <Box>
    <Text fontSize="sm" color="gray.600">
      {label}
    </Text>
    <Text fontSize="md" fontWeight="medium">
      {value}
    </Text>
  </Box>
);

export const PurchaseOrderDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();

  const {
    data: order,
    isLoading,
    error,
    refetch
  } = useQuery<PurchaseOrder>(
    ['purchase-orders', id],
    () => purchaseOrdersApi.get(Number(id)),
    {
      enabled: !!id,
      onError: (error) => {
        toast({
          title: 'Error loading purchase order',
          description: error.message,
          status: 'error',
          duration: 5000
        });
      }
    }
  );

  const submitMutation = useMutation(
    () => purchaseOrdersApi.submit(Number(id)),
    {
      onSuccess: () => {
        toast({
          title: 'Purchase order submitted',
          status: 'success',
          duration: 3000
        });
        refetch();
      },
      onError: (error) => {
        toast({
          title: 'Error submitting purchase order',
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

  if (error || !order) {
    return (
      <Box
        p={4}
        bg="red.50"
        color="red.500"
        borderRadius="md"
      >
        <Text>Error loading purchase order details</Text>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <HStack justify="space-between">
        <VStack align="start" spacing={1}>
          <Heading size="lg">
            Purchase Order #{order.id}
          </Heading>
          <Badge
            colorScheme={statusColors[order.status]}
            fontSize="sm"
          >
            {order.status}
          </Badge>
        </VStack>
        <HStack>
          {order.status === 'draft' && (
            <ButtonGroup>
              <Button
                colorScheme="blue"
                onClick={() => submitMutation.mutate()}
                isLoading={submitMutation.isLoading}
              >
                Submit for Approval
              </Button>
              <Button
                as={RouterLink}
                to={`/purchase-orders/${order.id}/edit`}
                variant="outline"
              >
                Edit
              </Button>
            </ButtonGroup>
          )}
          {order.status === 'approved' && (
            <Button
              as={RouterLink}
              to={`/purchase-orders/${order.id}/receive`}
              colorScheme="green"
            >
              Receive Items
            </Button>
          )}
          <Button
            onClick={() => navigate('/purchase-orders')}
            variant="ghost"
          >
            Back to List
          </Button>
        </HStack>
      </HStack>

      <Grid
        templateColumns="repeat(2, 1fr)"
        gap={6}
      >
        <Card>
          <CardHeader>
            <Heading size="md">
              Order Information
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <FieldDisplay
                label="Vendor ID"
                value={order.vendorId}
              />
              <FieldDisplay
                label="Created By"
                value={order.createdBy}
              />
              <FieldDisplay
                label="Created At"
                value={new Date(
                  order.createdAt
                ).toLocaleString()}
              />
              <FieldDisplay
                label="Total Amount"
                value={`$${order.total.toFixed(2)}`}
              />
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">
              Status Information
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              {order.submittedBy && (
                <>
                  <FieldDisplay
                    label="Submitted By"
                    value={order.submittedBy}
                  />
                  <FieldDisplay
                    label="Submitted At"
                    value={new Date(
                      order.submittedAt!
                    ).toLocaleString()}
                  />
                </>
              )}
              {order.approvedBy && (
                <>
                  <FieldDisplay
                    label="Approved By"
                    value={order.approvedBy}
                  />
                  <FieldDisplay
                    label="Approved At"
                    value={new Date(
                      order.approvedAt!
                    ).toLocaleString()}
                  />
                </>
              )}
              {order.receivedBy && (
                <>
                  <FieldDisplay
                    label="Received By"
                    value={order.receivedBy}
                  />
                  <FieldDisplay
                    label="Received At"
                    value={new Date(
                      order.receivedAt!
                    ).toLocaleString()}
                  />
                </>
              )}
            </VStack>
          </CardBody>
        </Card>
      </Grid>

      <Card>
        <CardHeader>
          <Heading size="md">Order Items</Heading>
        </CardHeader>
        <CardBody>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Item</Th>
                <Th isNumeric>Quantity</Th>
                <Th isNumeric>Price</Th>
                <Th isNumeric>Total</Th>
                {order.status === 'received' && (
                  <Th>Received</Th>
                )}
              </Tr>
            </Thead>
            <Tbody>
              {order.items.map((item, index) => (
                <Tr key={index}>
                  <Td>{item.name}</Td>
                  <Td isNumeric>{item.quantity}</Td>
                  <Td isNumeric>
                    ${item.price.toFixed(2)}
                  </Td>
                  <Td isNumeric>
                    ${(item.quantity * item.price).toFixed(2)}
                  </Td>
                  {order.status === 'received' && (
                    <Td>
                      <Badge
                        colorScheme={
                          item.received ? 'green' : 'red'
                        }
                      >
                        {item.received ? 'Yes' : 'No'}
                      </Badge>
                    </Td>
                  )}
                </Tr>
              ))}
            </Tbody>
          </Table>
        </CardBody>
      </Card>

      {order.notes && (
        <Card>
          <CardHeader>
            <Heading size="md">Notes</Heading>
          </CardHeader>
          <CardBody>
            <Text>{order.notes}</Text>
          </CardBody>
        </Card>
      )}
    </VStack>
  );
};

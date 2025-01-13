/**
 * Deposit detail component
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
  Divider,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Grid,
  GridItem,
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import { depositsApi } from '../../api/misc';
import { Deposit } from '../../types';

const statusColors = {
  pending: 'yellow',
  completed: 'green',
  failed: 'red'
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

export const DepositDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();

  const {
    data: deposit,
    isLoading,
    error
  } = useQuery<Deposit>(
    ['deposits', id],
    () => depositsApi.get(Number(id)),
    {
      enabled: !!id,
      onError: (error) => {
        toast({
          title: 'Error loading deposit',
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

  if (error || !deposit) {
    return (
      <Box
        p={4}
        bg="red.50"
        color="red.500"
        borderRadius="md"
      >
        <Text>Error loading deposit details</Text>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <HStack justify="space-between">
        <VStack align="start" spacing={1}>
          <Heading size="lg">
            Deposit #{deposit.id}
          </Heading>
          <Badge
            colorScheme={statusColors[deposit.status]}
            fontSize="sm"
          >
            {deposit.status}
          </Badge>
        </VStack>
        <HStack>
          <Button
            as={RouterLink}
            to={`/deposits/${deposit.id}/edit`}
            colorScheme="blue"
            variant="outline"
          >
            Edit
          </Button>
          <Button
            onClick={() => navigate('/deposits')}
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
              Deposit Information
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <FieldDisplay
                label="Amount"
                value={`$${deposit.amount.toFixed(2)}`}
              />
              <FieldDisplay
                label="Payment Method"
                value={deposit.paymentMethod}
              />
              <FieldDisplay
                label="Customer ID"
                value={deposit.customerId}
              />
              <FieldDisplay
                label="Created At"
                value={new Date(
                  deposit.createdAt
                ).toLocaleString()}
              />
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">
              Transaction Details
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <FieldDisplay
                label="Transaction ID"
                value={deposit.transactionId || 'N/A'}
              />
              <FieldDisplay
                label="Reference Number"
                value={deposit.referenceNumber || 'N/A'}
              />
              {deposit.notes && (
                <>
                  <Divider />
                  <Box>
                    <Text
                      fontSize="sm"
                      color="gray.600"
                      mb={1}
                    >
                      Notes
                    </Text>
                    <Text>{deposit.notes}</Text>
                  </Box>
                </>
              )}
            </VStack>
          </CardBody>
        </Card>
      </Grid>

      {deposit.status === 'failed' && (
        <Card bg="red.50">
          <CardHeader>
            <Heading size="md" color="red.500">
              Error Information
            </Heading>
          </CardHeader>
          <CardBody>
            <Text color="red.500">
              {deposit.errorMessage || 'No error details available'}
            </Text>
          </CardBody>
        </Card>
      )}
    </VStack>
  );
};

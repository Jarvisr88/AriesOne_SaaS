/**
 * Void detail component
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
  GridItem,
  Alert,
  AlertIcon,
  ButtonGroup,
} from '@chakra-ui/react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import { voidsApi } from '../../api/misc';
import { Void } from '../../types';

const statusColors = {
  pending: 'yellow',
  approved: 'green',
  rejected: 'red'
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

export const VoidDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();

  const {
    data: voidRequest,
    isLoading,
    error,
    refetch
  } = useQuery<Void>(
    ['voids', id],
    () => voidsApi.get(Number(id)),
    {
      enabled: !!id,
      onError: (error) => {
        toast({
          title: 'Error loading void request',
          description: error.message,
          status: 'error',
          duration: 5000
        });
      }
    }
  );

  const approveMutation = useMutation(
    () => voidsApi.approve(Number(id)),
    {
      onSuccess: () => {
        toast({
          title: 'Void request approved',
          status: 'success',
          duration: 3000
        });
        refetch();
      },
      onError: (error) => {
        toast({
          title: 'Error approving void request',
          description: error.message,
          status: 'error',
          duration: 5000
        });
      }
    }
  );

  const rejectMutation = useMutation(
    () => voidsApi.reject(Number(id)),
    {
      onSuccess: () => {
        toast({
          title: 'Void request rejected',
          status: 'success',
          duration: 3000
        });
        refetch();
      },
      onError: (error) => {
        toast({
          title: 'Error rejecting void request',
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

  if (error || !voidRequest) {
    return (
      <Box
        p={4}
        bg="red.50"
        color="red.500"
        borderRadius="md"
      >
        <Text>Error loading void request details</Text>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <HStack justify="space-between">
        <VStack align="start" spacing={1}>
          <Heading size="lg">
            Void Request #{voidRequest.id}
          </Heading>
          <Badge
            colorScheme={statusColors[voidRequest.status]}
            fontSize="sm"
          >
            {voidRequest.status}
          </Badge>
        </VStack>
        <HStack>
          {voidRequest.status === 'pending' && (
            <ButtonGroup>
              <Button
                colorScheme="green"
                onClick={() => approveMutation.mutate()}
                isLoading={approveMutation.isLoading}
              >
                Approve
              </Button>
              <Button
                colorScheme="red"
                variant="outline"
                onClick={() => rejectMutation.mutate()}
                isLoading={rejectMutation.isLoading}
              >
                Reject
              </Button>
            </ButtonGroup>
          )}
          {voidRequest.status === 'pending' && (
            <Button
              as={RouterLink}
              to={`/voids/${voidRequest.id}/edit`}
              colorScheme="blue"
              variant="outline"
            >
              Edit
            </Button>
          )}
          <Button
            onClick={() => navigate('/voids')}
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
              Void Request Information
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <FieldDisplay
                label="Amount"
                value={`$${voidRequest.amount.toFixed(2)}`}
              />
              <Box>
                <Text fontSize="sm" color="gray.600">
                  Reason
                </Text>
                <Text>{voidRequest.reason}</Text>
              </Box>
              <FieldDisplay
                label="Created By"
                value={voidRequest.createdBy}
              />
              <FieldDisplay
                label="Created At"
                value={new Date(
                  voidRequest.createdAt
                ).toLocaleString()}
              />
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">
              Review Information
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              {voidRequest.reviewedBy && (
                <>
                  <FieldDisplay
                    label="Reviewed By"
                    value={voidRequest.reviewedBy}
                  />
                  <FieldDisplay
                    label="Reviewed At"
                    value={new Date(
                      voidRequest.reviewedAt!
                    ).toLocaleString()}
                  />
                </>
              )}
              {voidRequest.comments && (
                <Box>
                  <Text
                    fontSize="sm"
                    color="gray.600"
                    mb={1}
                  >
                    Review Comments
                  </Text>
                  <Text>{voidRequest.comments}</Text>
                </Box>
              )}
              {!voidRequest.reviewedBy && (
                <Alert status="info">
                  <AlertIcon />
                  This void request is pending review
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>
      </Grid>
    </VStack>
  );
};

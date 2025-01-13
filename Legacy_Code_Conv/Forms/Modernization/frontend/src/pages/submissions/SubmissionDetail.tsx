/**
 * Submission detail page.
 * 
 * This page displays a form submission with approval workflow.
 */
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Flex,
  Heading,
  VStack,
  HStack,
  Badge,
  Text,
  useColorModeValue,
  useToast,
  Divider,
  Grid,
  GridItem,
  Card,
  CardHeader,
  CardBody,
} from '@chakra-ui/react';
import {
  useSubmissionDetail,
  useUpdateSubmission,
} from '../../hooks/useSubmissionQuery';
import { LoadingState } from '../../components/shared/LoadingState';


export const SubmissionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  
  const submissionId = parseInt(id || '0');
  const {
    data: submission,
    isLoading,
    error,
  } = useSubmissionDetail(submissionId);
  const updateSubmission = useUpdateSubmission();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  const handleAction = async (action: 'approve' | 'reject') => {
    try {
      await updateSubmission.mutateAsync({
        id: submissionId,
        data: {
          status: action === 'approve' ? 'approved' : 'rejected',
        },
      });
      
      toast({
        title: 'Success',
        description: `Submission ${action}d successfully`,
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: `Failed to ${action} submission`,
        status: 'error',
        duration: 3000,
      });
    }
  };
  
  if (isLoading) {
    return <LoadingState text="Loading submission..." />;
  }
  
  if (error || !submission) {
    return (
      <Box
        p={4}
        bg="red.50"
        color="red.500"
        borderRadius="md"
        textAlign="center"
      >
        Failed to load submission
      </Box>
    );
  }
  
  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <VStack align="start" spacing={1}>
          <Heading size="lg">
            {submission.form_name}
          </Heading>
          <Text color="gray.500">
            Submission #{submission.id}
          </Text>
        </VStack>
        
        <HStack spacing={4}>
          <Button
            onClick={() => navigate('/submissions')}
            variant="ghost"
          >
            Back to List
          </Button>
          <Button
            onClick={() => {
              // Handle download
            }}
          >
            Download PDF
          </Button>
        </HStack>
      </Flex>
      
      <Grid templateColumns="3fr 1fr" gap={6}>
        <GridItem>
          <Card bg={bgColor} shadow="base">
            <CardHeader>
              <Heading size="md">Form Data</Heading>
            </CardHeader>
            <CardBody>
              {/* Render form fields dynamically */}
              {Object.entries(submission.data).map(([key, value]) => (
                <Box key={key} mb={4}>
                  <Text
                    fontSize="sm"
                    fontWeight="medium"
                    color="gray.500"
                    mb={1}
                  >
                    {key}
                  </Text>
                  <Text>{String(value)}</Text>
                </Box>
              ))}
            </CardBody>
          </Card>
        </GridItem>
        
        <GridItem>
          <VStack spacing={6}>
            <Card bg={bgColor} shadow="base" w="full">
              <CardHeader>
                <Heading size="md">Status</Heading>
              </CardHeader>
              <CardBody>
                <VStack align="stretch" spacing={4}>
                  <Box>
                    <Text
                      fontSize="sm"
                      color="gray.500"
                      mb={1}
                    >
                      Current Status
                    </Text>
                    <Badge
                      colorScheme={{
                        pending: 'yellow',
                        approved: 'green',
                        rejected: 'red',
                      }[submission.status]}
                      fontSize="md"
                      px={2}
                      py={1}
                    >
                      {submission.status}
                    </Badge>
                  </Box>
                  
                  <Divider />
                  
                  {submission.status === 'pending' && (
                    <VStack spacing={3}>
                      <Button
                        colorScheme="green"
                        w="full"
                        onClick={() => handleAction('approve')}
                        isLoading={updateSubmission.isPending}
                      >
                        Approve
                      </Button>
                      <Button
                        colorScheme="red"
                        variant="outline"
                        w="full"
                        onClick={() => handleAction('reject')}
                        isLoading={updateSubmission.isPending}
                      >
                        Reject
                      </Button>
                    </VStack>
                  )}
                </VStack>
              </CardBody>
            </Card>
            
            <Card bg={bgColor} shadow="base" w="full">
              <CardHeader>
                <Heading size="md">Details</Heading>
              </CardHeader>
              <CardBody>
                <VStack align="stretch" spacing={4}>
                  <Box>
                    <Text
                      fontSize="sm"
                      color="gray.500"
                      mb={1}
                    >
                      Submitted By
                    </Text>
                    <Text>{submission.submitted_by}</Text>
                  </Box>
                  
                  <Box>
                    <Text
                      fontSize="sm"
                      color="gray.500"
                      mb={1}
                    >
                      Submitted At
                    </Text>
                    <Text>
                      {new Date(submission.submitted_at).toLocaleString()}
                    </Text>
                  </Box>
                  
                  {submission.company_name && (
                    <Box>
                      <Text
                        fontSize="sm"
                        color="gray.500"
                        mb={1}
                      >
                        Company
                      </Text>
                      <Text>{submission.company_name}</Text>
                    </Box>
                  )}
                </VStack>
              </CardBody>
            </Card>
          </VStack>
        </GridItem>
      </Grid>
    </Box>
  );
};

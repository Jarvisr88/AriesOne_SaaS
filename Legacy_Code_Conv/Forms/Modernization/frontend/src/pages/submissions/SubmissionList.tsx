/**
 * Submission list page.
 * 
 * This page displays a list of form submissions with filtering.
 */
import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Flex,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Link,
  Text,
  useColorModeValue,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  HStack,
  Select,
  Input,
} from '@chakra-ui/react';
import {
  ViewIcon,
  DownloadIcon,
  SettingsIcon,
} from '@chakra-ui/icons';
import { useSubmissionList } from '../../hooks/useSubmissionQuery';
import { LoadingState } from '../../components/shared/LoadingState';


export const SubmissionList: React.FC = () => {
  const [formId, setFormId] = React.useState<string>('');
  const [status, setStatus] = React.useState<string>('');
  const [search, setSearch] = React.useState<string>('');
  
  const {
    data: submissions,
    isLoading,
    error,
  } = useSubmissionList({
    formId: formId ? parseInt(formId) : undefined,
    status,
    search,
  });
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  if (isLoading) {
    return <LoadingState text="Loading submissions..." />;
  }
  
  if (error) {
    return (
      <Box
        p={4}
        bg="red.50"
        color="red.500"
        borderRadius="md"
        textAlign="center"
      >
        Failed to load submissions
      </Box>
    );
  }
  
  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Submissions</Heading>
        <Button
          leftIcon={<DownloadIcon />}
          colorScheme="blue"
        >
          Export
        </Button>
      </Flex>
      
      <Box mb={6}>
        <HStack spacing={4}>
          <Select
            value={formId}
            onChange={(e) => setFormId(e.target.value)}
            placeholder="All Forms"
            w="200px"
          >
            {/* Form options would be populated here */}
          </Select>
          
          <Select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            placeholder="All Statuses"
            w="200px"
          >
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </Select>
          
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search submissions..."
            w="300px"
          />
        </HStack>
      </Box>
      
      {submissions?.length === 0 ? (
        <Box
          p={8}
          bg={bgColor}
          borderWidth={1}
          borderColor={borderColor}
          borderRadius="md"
          textAlign="center"
        >
          <Text color="gray.500">
            No submissions found
          </Text>
        </Box>
      ) : (
        <Box
          bg={bgColor}
          borderWidth={1}
          borderColor={borderColor}
          borderRadius="md"
          overflow="hidden"
        >
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Form</Th>
                <Th>Submitted By</Th>
                <Th>Status</Th>
                <Th>Submitted</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {submissions?.map((submission) => (
                <Tr key={submission.id}>
                  <Td>
                    <Link
                      as={RouterLink}
                      to={`/submissions/${submission.id}`}
                      color="blue.500"
                      fontWeight="medium"
                    >
                      {submission.form_name}
                    </Link>
                    {submission.company_name && (
                      <Text
                        fontSize="sm"
                        color="gray.500"
                      >
                        {submission.company_name}
                      </Text>
                    )}
                  </Td>
                  <Td>{submission.submitted_by}</Td>
                  <Td>
                    <Badge
                      colorScheme={{
                        pending: 'yellow',
                        approved: 'green',
                        rejected: 'red',
                      }[submission.status]}
                    >
                      {submission.status}
                    </Badge>
                  </Td>
                  <Td>
                    {new Date(submission.submitted_at).toLocaleDateString()}
                  </Td>
                  <Td>
                    <Flex gap={2}>
                      <IconButton
                        as={RouterLink}
                        to={`/submissions/${submission.id}`}
                        aria-label="View submission"
                        icon={<ViewIcon />}
                        size="sm"
                        variant="ghost"
                      />
                      <Menu>
                        <MenuButton
                          as={IconButton}
                          aria-label="More options"
                          icon={<SettingsIcon />}
                          size="sm"
                          variant="ghost"
                        />
                        <MenuList>
                          <MenuItem
                            onClick={() => {
                              // Handle download
                            }}
                          >
                            Download PDF
                          </MenuItem>
                          <MenuItem
                            as={RouterLink}
                            to={`/submissions/${submission.id}/history`}
                          >
                            View History
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    </Flex>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}
    </Box>
  );
};

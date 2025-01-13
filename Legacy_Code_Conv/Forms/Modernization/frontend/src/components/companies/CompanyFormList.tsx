/**
 * Company form list component.
 * 
 * This component displays forms assigned to a company.
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
  Spinner,
  Text,
  useColorModeValue,
  IconButton,
} from '@chakra-ui/react';
import { ViewIcon, EditIcon } from '@chakra-ui/icons';
import { useCompanyForms } from '../../hooks/useCompanyQuery';


interface CompanyFormListProps {
  companyId: number;
}

export const CompanyFormList: React.FC<CompanyFormListProps> = ({
  companyId,
}) => {
  const {
    data: forms,
    isLoading,
    error,
  } = useCompanyForms(companyId);
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  if (isLoading) {
    return (
      <Flex justify="center" align="center" minH="200px">
        <Spinner />
      </Flex>
    );
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
        Failed to load company forms
      </Box>
    );
  }
  
  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="md">Assigned Forms</Heading>
        <Button
          as={RouterLink}
          to={`/companies/${companyId}/forms/assign`}
          colorScheme="blue"
          size="sm"
        >
          Assign Form
        </Button>
      </Flex>
      
      {forms?.length === 0 ? (
        <Box
          p={8}
          bg={bgColor}
          borderWidth={1}
          borderColor={borderColor}
          borderRadius="md"
          textAlign="center"
        >
          <Text color="gray.500" mb={4}>
            No forms assigned to this company
          </Text>
          <Button
            as={RouterLink}
            to={`/companies/${companyId}/forms/assign`}
            colorScheme="blue"
            size="sm"
          >
            Assign your first form
          </Button>
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
                <Th>Form Name</Th>
                <Th>Status</Th>
                <Th>Submissions</Th>
                <Th>Last Updated</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {forms?.map((form) => (
                <Tr key={form.id}>
                  <Td>
                    <Link
                      as={RouterLink}
                      to={`/companies/${companyId}/forms/${form.form_id}`}
                      color="blue.500"
                      fontWeight="medium"
                    >
                      {form.form_name}
                    </Link>
                  </Td>
                  <Td>
                    <Badge
                      colorScheme={form.is_active ? 'green' : 'gray'}
                    >
                      {form.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </Td>
                  <Td>{form.submission_count || 0}</Td>
                  <Td>
                    {new Date(form.updated_at).toLocaleDateString()}
                  </Td>
                  <Td>
                    <Flex gap={2}>
                      <IconButton
                        as={RouterLink}
                        to={`/companies/${companyId}/forms/${form.form_id}`}
                        aria-label="View form"
                        icon={<ViewIcon />}
                        size="sm"
                        variant="ghost"
                      />
                      <IconButton
                        as={RouterLink}
                        to={`/companies/${companyId}/forms/${form.form_id}/settings`}
                        aria-label="Edit settings"
                        icon={<EditIcon />}
                        size="sm"
                        variant="ghost"
                      />
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

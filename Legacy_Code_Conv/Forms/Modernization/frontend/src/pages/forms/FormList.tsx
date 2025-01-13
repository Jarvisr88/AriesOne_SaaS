/**
 * Form list page.
 * 
 * This page displays a list of all forms with filtering and sorting.
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
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
} from '@chakra-ui/react';
import {
  AddIcon,
  EditIcon,
  ViewIcon,
  SettingsIcon,
} from '@chakra-ui/icons';
import { useFormList } from '../../hooks/useFormQuery';
import { Form } from '../../types/forms';


export const FormList: React.FC = () => {
  const { data: forms, isLoading, error } = useFormList();
  
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
        Failed to load forms
      </Box>
    );
  }
  
  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Forms</Heading>
        <Button
          as={RouterLink}
          to="/forms/new"
          colorScheme="blue"
          leftIcon={<AddIcon />}
        >
          Create Form
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
            No forms found
          </Text>
          <Button
            as={RouterLink}
            to="/forms/new"
            colorScheme="blue"
            size="sm"
          >
            Create your first form
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
                <Th>Name</Th>
                <Th>Created By</Th>
                <Th>Status</Th>
                <Th>Created</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {forms?.map((form: Form) => (
                <Tr key={form.id}>
                  <Td>
                    <Link
                      as={RouterLink}
                      to={`/forms/${form.id}`}
                      color="blue.500"
                      fontWeight="medium"
                    >
                      {form.name}
                    </Link>
                    {form.description && (
                      <Text
                        fontSize="sm"
                        color="gray.500"
                        noOfLines={1}
                      >
                        {form.description}
                      </Text>
                    )}
                  </Td>
                  <Td>User {form.created_by}</Td>
                  <Td>
                    <Badge
                      colorScheme={form.is_active ? 'green' : 'gray'}
                    >
                      {form.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </Td>
                  <Td>
                    {new Date(form.created_at).toLocaleDateString()}
                  </Td>
                  <Td>
                    <Flex gap={2}>
                      <IconButton
                        as={RouterLink}
                        to={`/forms/${form.id}`}
                        aria-label="View form"
                        icon={<ViewIcon />}
                        size="sm"
                        variant="ghost"
                      />
                      <IconButton
                        as={RouterLink}
                        to={`/forms/${form.id}/edit`}
                        aria-label="Edit form"
                        icon={<EditIcon />}
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
                            as={RouterLink}
                            to={`/forms/${form.id}/submissions`}
                          >
                            View Submissions
                          </MenuItem>
                          <MenuItem
                            as={RouterLink}
                            to={`/forms/${form.id}/settings`}
                          >
                            Form Settings
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

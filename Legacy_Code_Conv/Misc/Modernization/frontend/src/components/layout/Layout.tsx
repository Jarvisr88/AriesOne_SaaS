/**
 * Main application layout component
 */
import React from 'react';
import {
  Box,
  Container,
  Flex,
  VStack,
  useColorModeValue
} from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Breadcrumbs } from './Breadcrumbs';
import { ErrorBoundary } from '../common/ErrorBoundary';

export const Layout: React.FC = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');

  return (
    <Flex
      minH="100vh"
      direction="column"
      bg={bgColor}
    >
      <Navbar />
      <Container
        maxW="container.xl"
        flex={1}
        py={6}
      >
        <VStack spacing={6} align="stretch">
          <Breadcrumbs />
          <Box
            bg="white"
            borderRadius="lg"
            boxShadow="sm"
            p={6}
          >
            <ErrorBoundary>
              <Outlet />
            </ErrorBoundary>
          </Box>
        </VStack>
      </Container>
    </Flex>
  );
};

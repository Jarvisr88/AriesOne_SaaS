/**
 * Layout component.
 * 
 * This component provides the main application layout.
 */
import React from 'react';
import { Box, useColorModeValue } from '@chakra-ui/react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { ErrorBoundary } from '../shared/ErrorBoundary';


interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  
  return (
    <Box minH="100vh" bg={bgColor}>
      <Header />
      <Sidebar />
      
      <Box
        as="main"
        ml={64}
        mt={16}
        p={8}
      >
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </Box>
    </Box>
  );
};

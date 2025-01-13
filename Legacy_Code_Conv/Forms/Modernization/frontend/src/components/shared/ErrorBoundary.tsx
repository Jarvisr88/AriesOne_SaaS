/**
 * Error boundary component.
 * 
 * This component catches and handles React errors.
 */
import React from 'react';
import {
  Box,
  Button,
  Heading,
  Text,
  VStack,
  useColorModeValue,
} from '@chakra-ui/react';


interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box
          p={8}
          bg={useColorModeValue('white', 'gray.800')}
          borderRadius="lg"
          shadow="base"
        >
          <VStack spacing={4} align="center">
            <Heading size="lg" color="red.500">
              Something went wrong
            </Heading>
            
            <Text color="gray.500">
              {this.state.error?.message || 'An error occurred'}
            </Text>
            
            <Button
              colorScheme="blue"
              onClick={() => window.location.reload()}
            >
              Reload Page
            </Button>
          </VStack>
        </Box>
      );
    }

    return this.props.children;
  }
}

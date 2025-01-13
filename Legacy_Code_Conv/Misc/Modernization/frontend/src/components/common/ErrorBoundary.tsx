/**
 * Error boundary component for handling React errors
 */
import React from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Button,
  Code,
  useToast
} from '@chakra-ui/react';

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to monitoring service
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box
          p={8}
          maxW="container.md"
          mx="auto"
          textAlign="center"
        >
          <VStack spacing={6}>
            <Heading color="red.500">
              Something went wrong
            </Heading>
            <Text>
              We apologize for the inconvenience. Please try refreshing the page or contact support if the problem persists.
            </Text>
            {this.state.error && (
              <Code p={4} borderRadius="md" bg="red.50">
                {this.state.error.message}
              </Code>
            )}
            <Button
              colorScheme="blue"
              onClick={() => window.location.reload()}
            >
              Refresh Page
            </Button>
          </VStack>
        </Box>
      );
    }

    return this.props.children;
  }
}

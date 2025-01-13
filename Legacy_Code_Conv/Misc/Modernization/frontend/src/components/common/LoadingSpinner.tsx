/**
 * Loading spinner component
 */
import React from 'react';
import {
  Box,
  Spinner,
  Text,
  VStack
} from '@chakra-ui/react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  fullPage?: boolean;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  size = 'lg',
  fullPage = false
}) => {
  const content = (
    <VStack spacing={4}>
      <Spinner
        size={size}
        thickness="4px"
        speed="0.65s"
        color="blue.500"
      />
      {message && (
        <Text color="gray.600">
          {message}
        </Text>
      )}
    </VStack>
  );

  if (fullPage) {
    return (
      <Box
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        display="flex"
        alignItems="center"
        justifyContent="center"
        bg="whiteAlpha.900"
        zIndex={9999}
      >
        {content}
      </Box>
    );
  }

  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      p={8}
    >
      {content}
    </Box>
  );
};

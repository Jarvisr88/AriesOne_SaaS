/**
 * Loading state component.
 * 
 * This component provides a consistent loading indicator.
 */
import React from 'react';
import {
  Box,
  Flex,
  Spinner,
  Text,
  useColorModeValue,
} from '@chakra-ui/react';


interface LoadingStateProps {
  text?: string;
  size?: 'sm' | 'md' | 'lg';
  fullPage?: boolean;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  text = 'Loading...',
  size = 'md',
  fullPage = false,
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const spinnerSize = {
    sm: 'md',
    md: 'lg',
    lg: 'xl',
  }[size];
  
  const content = (
    <Flex
      direction="column"
      align="center"
      justify="center"
      p={8}
      minH={size === 'sm' ? '100px' : '200px'}
    >
      <Spinner
        size={spinnerSize}
        color="blue.500"
        thickness="3px"
        mb={4}
      />
      {text && (
        <Text
          color="gray.500"
          fontSize={size === 'sm' ? 'sm' : 'md'}
        >
          {text}
        </Text>
      )}
    </Flex>
  );
  
  if (fullPage) {
    return (
      <Flex
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        bg={bgColor}
        zIndex={9999}
        align="center"
        justify="center"
      >
        {content}
      </Flex>
    );
  }
  
  return (
    <Box
      bg={bgColor}
      borderRadius="lg"
      shadow="base"
    >
      {content}
    </Box>
  );
};

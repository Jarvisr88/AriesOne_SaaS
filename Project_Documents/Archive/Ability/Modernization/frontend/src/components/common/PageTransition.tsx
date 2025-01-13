import React from 'react';
import { SlideFade, Box } from '@chakra-ui/react';

interface PageTransitionProps {
  children: React.ReactNode;
}

export const PageTransition: React.FC<PageTransitionProps> = ({ children }) => {
  return (
    <SlideFade in offsetY={20}>
      <Box>{children}</Box>
    </SlideFade>
  );
};

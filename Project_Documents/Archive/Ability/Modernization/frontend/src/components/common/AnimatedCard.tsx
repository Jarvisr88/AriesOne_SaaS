import React from 'react';
import { Box, BoxProps } from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';

const MotionBox = motion(Box);

interface AnimatedCardProps extends BoxProps {
  children: React.ReactNode;
  delay?: number;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  delay = 0,
  ...props
}) => {
  return (
    <AnimatePresence>
      <MotionBox
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{
          duration: 0.3,
          delay,
          ease: 'easeOut',
        }}
        p={6}
        bg="bg.primary"
        borderRadius="xl"
        boxShadow="lg"
        border="1px solid"
        borderColor="border.primary"
        _hover={{
          transform: 'translateY(-2px)',
          boxShadow: 'xl',
          transition: 'all 0.2s',
        }}
        role="group"
        {...props}
      >
        {children}
      </MotionBox>
    </AnimatePresence>
  );
};
